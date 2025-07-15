import hashlib
import time
from PIL import ImageGrab
import numpy as np


class PerceptionController:
    last_hash = None  # Used for change detection between frames

    @staticmethod
    def get_active_pixels(bbox=None):
        """
        Capture raw RGB pixels from full screen or specified region.
        Returns both pixel array and PIL image.
        """
        image = ImageGrab.grab(bbox=bbox)
        pixels = np.array(image)
        return pixels, image

    @staticmethod
    def hash_pixels(pixels):
        """
        Create SHA1 hash of the image for change detection.
        """
        return hashlib.sha1(pixels.tobytes()).hexdigest()

    @staticmethod
    def has_screen_changed(pixels):
        """
        Compare current screen hash to the last known hash.
        Returns True if changed, otherwise False.
        """
        current_hash = PerceptionController.hash_pixels(pixels)
        changed = current_hash != PerceptionController.last_hash
        if changed:
            PerceptionController.last_hash = current_hash
        return changed

    @staticmethod
    def capture_screen_array():
        """
        Wrapper for PosterAgent & others.
        Simply returns a fresh raw RGB screen pixel array.
        """
        pixels, _ = PerceptionController.get_active_pixels()
        return pixels
