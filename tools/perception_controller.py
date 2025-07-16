# tools/perception_controller.py

import hashlib
import numpy as np
import mss
import mss.tools
import pygetwindow as gw
import time
from PIL import Image

class PerceptionController:
    last_hash = None  # Used for change detection

    @staticmethod
    def get_active_window_bbox():
        """
        Attempts to find the active window's bounding box (left, top, right, bottom).
        Falls back to primary screen if not found.
        """
        try:
            active = gw.getActiveWindow()
            if active is not None:
                return (
                    active.left,
                    active.top,
                    active.left + active.width,
                    active.top + active.height
                )
        except Exception as e:
            print(f"[PerceptionController] ⚠️ Failed to get active window: {e}")

        return None  # Fall back to full screen capture

    @staticmethod
    def get_active_pixels(bbox=None):
        """
        Capture raw RGB pixels from full screen or specific bounding box.
        Uses mss for fast native-resolution screen grab.
        Returns (pixels: np.array, image: PIL.Image)
        """
        with mss.mss() as sct:
            if bbox:
                monitor = {
                    "top": bbox[1],
                    "left": bbox[0],
                    "width": bbox[2] - bbox[0],
                    "height": bbox[3] - bbox[1],
                }
            else:
                monitor = sct.monitors[1]  # Primary screen

            sct_img = sct.grab(monitor)
            img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
            pixels = np.array(img)
            return pixels, img

    @staticmethod
    def hash_pixels(pixels):
        return hashlib.sha1(pixels.tobytes()).hexdigest()

    @staticmethod
    def has_screen_changed(pixels):
        current_hash = PerceptionController.hash_pixels(pixels)
        changed = current_hash != PerceptionController.last_hash
        if changed:
            PerceptionController.last_hash = current_hash
        return changed

    @staticmethod
    def capture_screen_array(force_fullscreen=False):
        """
        Captures screen pixels of active window or full screen.
        Returns raw RGB NumPy pixel array.
        """
        bbox = None
        if not force_fullscreen:
            bbox = PerceptionController.get_active_window_bbox()
        pixels, _ = PerceptionController.get_active_pixels(bbox=bbox)
        return pixels
