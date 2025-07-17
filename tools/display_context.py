# tools/display_context.py

import ctypes
import mss
import logging

# Configure logging for this module
logger = logging.getLogger(__name__)

class DisplayContext:
    """
    A reliable utility for fetching information about the user's display setup,
    focusing exclusively on the primary monitor for a stable coordinate system.
    """

    @staticmethod
    def get_scaling_factor() -> float:
        """
        Returns the display scaling factor for the primary monitor on Windows.
        (e.g., 1.25 for 125%). Returns 1.0 as a fallback.
        """
        try:
            # This method is specific to Windows
            user32 = ctypes.windll.user32
            # This call is necessary for the DPI functions to work correctly
            user32.SetProcessDPIAware()
            
            # Get the device context for the entire screen
            hdc = user32.GetDC(0)
            
            # 88 is the index for LOGPIXELSX, which gives the horizontal DPI
            LOGPIXELSX = 88
            dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, LOGPIXELSX)
            
            # Release the device context
            user32.ReleaseDC(0, hdc)
            
            # The default DPI is 96, which represents 100% scaling
            scaling_factor = dpi / 96.0
            logger.info(f"Detected display scaling factor: {scaling_factor}")
            return scaling_factor
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch DPI scaling factor, defaulting to 1.0. Error: {e}")
            return 1.0

    @staticmethod
    def get_primary_monitor_info() -> dict:
        """
        Returns a dictionary containing the geometry of the primary monitor.
        Keys: 'left', 'top', 'width', 'height'
        """
        try:
            with mss.mss() as sct:
                # sct.monitors[1] is the designated primary monitor
                primary_monitor = sct.monitors[1]
                return primary_monitor
        except Exception as e:
            logger.error(f"❌ Failed to get primary monitor info using mss: {e}")
            # Fallback to a default resolution if mss fails
            return {"left": 0, "top": 0, "width": 1920, "height": 1080}

    @staticmethod
    def describe() -> dict:
        """
        Returns a consolidated dictionary of all critical display information.
        """
        scaling = DisplayContext.get_scaling_factor()
        monitor_info = DisplayContext.get_primary_monitor_info()
        
        # Create a bounding box tuple for convenience
        bbox = (
            monitor_info["left"],
            monitor_info["top"],
            monitor_info["left"] + monitor_info["width"],
            monitor_info["top"] + monitor_info["height"]
        )

        return {
            "scaling_factor": scaling,
            "resolution": (monitor_info["width"], monitor_info["height"]),
            "bbox": bbox
        }

    @staticmethod
    def print_summary():
        """A utility function to print the display context for debugging."""
        info = DisplayContext.describe()
        print("\n--- [DisplayContext Summary] ---")
        print(f"  Scaling Factor: {info['scaling_factor']:.2f} ({info['scaling_factor'] * 100:.0f}%)")
        print(f"  Resolution:     {info['resolution'][0]}x{info['resolution'][1]}")
        print(f"  Bounding Box:   {info['bbox']}")
        print("--------------------------------\n")

