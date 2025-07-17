# tools/display_context.py

import ctypes
import mss
import pygetwindow as gw

class DisplayContext:
    @staticmethod
    def get_scaling_factor():
        """
        Returns Windows display scaling factor (e.g., 1.25 for 125%)
        """
        try:
            user32 = ctypes.windll.user32
            gdi32 = ctypes.windll.gdi32
            user32.SetProcessDPIAware()
            hdc = user32.GetDC(0)
            LOGPIXELSX = 88
            dpi = gdi32.GetDeviceCaps(hdc, LOGPIXELSX)
            return dpi / 96.0  # 96 DPI = 100%
        except Exception as e:
            print(f"[DisplayContext] ⚠️ DPI fetch failed: {e}")
            return 1.0

    @staticmethod
    def get_primary_monitor_bbox():
        """
        Returns bounding box of primary monitor: (left, top, right, bottom)
        """
        with mss.mss() as sct:
            m = sct.monitors[1]  # Primary
            return (m["left"], m["top"], m["left"] + m["width"], m["top"] + m["height"])

    @staticmethod
    def get_active_window_monitor_bbox():
        """
        Returns the monitor bbox that contains the active window.
        Falls back to primary if active window or monitor not detected.
        """
        try:
            active = gw.getActiveWindow()
            if not active:
                raise Exception("No active window")

            ax, ay = active.left, active.top

            with mss.mss() as sct:
                for m in sct.monitors[1:]:
                    mx1, my1 = m["left"], m["top"]
                    mx2 = mx1 + m["width"]
                    my2 = my1 + m["height"]
                    if mx1 <= ax <= mx2 and my1 <= ay <= my2:
                        return (mx1, my1, mx2, my2)

        except Exception as e:
            print(f"[DisplayContext] ⚠️ Failed to locate active monitor: {e}")

        # fallback to primary
        return DisplayContext.get_primary_monitor_bbox()

    @staticmethod
    def describe():
        """
        Returns full display info dictionary:
        - scaling factor
        - resolution of active monitor
        - monitor bbox
        """
        scale = DisplayContext.get_scaling_factor()
        bbox = DisplayContext.get_active_window_monitor_bbox()
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]

        return {
            "scaling_factor": scale,
            "resolution": f"{width}x{height}",
            "bbox": bbox
        }

    @staticmethod
    def print_summary():
        info = DisplayContext.describe()
        print("[🖥️ DisplayContext] Active Display Info:")
        print(f"   ↳ Resolution     : {info['resolution']}")
        print(f"   ↳ DPI Scaling    : {info['scaling_factor'] * 100:.0f}%")
        print(f"   ↳ Screen BBox    : {info['bbox']}")
