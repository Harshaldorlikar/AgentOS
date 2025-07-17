# tools/perception_controller.py

import hashlib
import numpy as np
import mss
from PIL import Image, ImageDraw
from datetime import datetime
from tools.display_context import DisplayContext
from tools.gemini_ui_vision import smart_vision_query  # ✅ Use new wrapper

class PerceptionController:
    last_hash = None
    last_capture_time = None

    @staticmethod
    def capture_screen_array():
        """Captures the screen of the active window's monitor."""
        try:
            bbox = DisplayContext.get_active_window_monitor_bbox()
            monitor = {
                "top": bbox[1],
                "left": bbox[0],
                "width": bbox[2] - bbox[0],
                "height": bbox[3] - bbox[1]
            }

            with mss.mss() as sct:
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
                pixels = np.array(img)
                return pixels, bbox
        except Exception as e:
            print(f"[PerceptionController] ❌ Screen capture failed: {e}")
            return None, None

    @staticmethod
    def hash_pixels(pixels):
        return hashlib.sha1(pixels.tobytes()).hexdigest()

    @staticmethod
    def has_screen_changed(pixels, log_changes=True):
        current_hash = PerceptionController.hash_pixels(pixels)
        changed = current_hash != PerceptionController.last_hash

        if changed:
            PerceptionController.last_hash = current_hash
            PerceptionController.last_capture_time = datetime.now()
            if log_changes:
                print(f"[PerceptionController] 🔄 Change detected at {PerceptionController.last_capture_time.strftime('%H:%M:%S.%f')[:-3]}")
        else:
            if log_changes:
                print(f"[PerceptionController] ⏸️ No visual change detected.")

        return changed

    @staticmethod
    def analyze_ui_elements(task_prompt: str, log=True):
        """
        Capture + Analyze current screen using Gemini vision.
        Only triggers analysis if screen has changed.
        """
        pixels, _ = PerceptionController.capture_screen_array()
        if pixels is None:
            return []

        if not PerceptionController.has_screen_changed(pixels, log_changes=log):
            if log:
                print("[PerceptionController] 👁️ Skipping Gemini call — screen unchanged.")
            return []

        results = smart_vision_query(pixels, task_prompt)
        return results

    @staticmethod
    def draw_debug_overlay(pixels, bbox, save_path="debug_screen_overlay.png"):
        try:
            img = Image.fromarray(pixels.copy(), "RGB")
            draw = ImageDraw.Draw(img)
            draw.rectangle([(0, 0), (pixels.shape[1] - 1, pixels.shape[0] - 1)], outline="red", width=4)
            img.save(save_path)
            print(f"[PerceptionController] 🖼️ Debug screenshot saved to {save_path}")
        except Exception as e:
            print(f"[PerceptionController] ⚠️ Failed to save debug screenshot: {e}")
