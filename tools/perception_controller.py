# tools/perception_controller.py

import hashlib
import numpy as np
import mss
import mss.tools
from PIL import Image
import os
import logging

# Configure logging for this module
logger = logging.getLogger(__name__)

class PerceptionController:
    """
    A robust controller for capturing screen data. It can capture the full
    primary monitor or a specific region of it, providing a stable foundation
    for the agent's vision system.
    """
    last_hash = None

    @staticmethod
    def capture_primary_monitor():
        """
        Captures the FULL PRIMARY MONITOR to ensure a consistent coordinate system.
        This is the most reliable method for multi-monitor setups.

        Returns:
            A tuple of (pixels, monitor_info_dict) or (None, None) on failure.
        """
        try:
            with mss.mss() as sct:
                # sct.monitors[1] is the designated primary monitor.
                primary_monitor = sct.monitors[1]
                sct_img = sct.grab(primary_monitor)
                
                # Convert to the format we need
                img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
                pixels = np.array(img)
                
                return pixels, primary_monitor
        except Exception as e:
            logger.error(f"Failed to capture primary monitor: {e}", exc_info=True)
            return None, None

    @staticmethod
    def capture_screen_region(bbox: dict):
        """
        ✅ NEW FUNCTION: Captures a specific region of the screen.
        This is essential for the two-step perception logic.
        The bounding box should be a dictionary with 'left', 'top', 'width', 'height'.
        """
        try:
            with mss.mss() as sct:
                sct_img = sct.grab(bbox)
                img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
                pixels = np.array(img)
                # The bbox for a region capture is the region itself
                return pixels, bbox
        except Exception as e:
            logger.error(f"Failed to capture screen region at {bbox}: {e}", exc_info=True)
            return None, None

    @staticmethod
    def hash_pixels(pixels: np.array) -> str:
        """Creates a SHA1 hash of the pixel array for fast change detection."""
        return hashlib.sha1(pixels.tobytes()).hexdigest()

    @staticmethod
    def has_screen_changed(pixels: np.array) -> bool:
        """Compares the current screen hash to the last known hash."""
        current_hash = PerceptionController.hash_pixels(pixels)
        if current_hash != PerceptionController.last_hash:
            PerceptionController.last_hash = current_hash
            return True
        return False

    @staticmethod
    def save_screen_snapshot(pixels: np.array, save_path: str) -> bool:
        """Saves a screenshot from a given pixel array for debugging."""
        if pixels is None:
            logger.error("No pixels to save.")
            return False
        try:
            img = Image.fromarray(pixels.copy(), "RGB")
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            img.save(save_path)
            logger.info(f"📸 Debug screenshot saved to {save_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save screenshot to {save_path}: {e}", exc_info=True)
            return False
