import hashlib
import time
from PIL import ImageGrab, Image
import numpy as np
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_CLI = os.getenv("GEMINI_CLI")  # Path to Gemini CLI 2.5


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
    def ask_gemini_with_pixels(pixels, reasoning_prompt="Identify visible UI components and clickable elements."):
        """
        Feed raw RGB pixel array to Gemini via CLI with a reasoning prompt.
        Converts to downscaled array for efficiency and formats prompt.
        """
        # Optional Downscaling for token cost
        if pixels.shape[0] > 500:
            img = Image.fromarray(pixels)
            img = img.resize((400, 300))
            pixels = np.array(img)

        # Convert to trimmed list of pixels
        flat_rgb = pixels.tolist()[:3000]  # Truncate for token limit

        prompt = f"""
You are a computer vision AI agent perceiving the world through raw RGB pixel data.
Each pixel is represented as a list: [R, G, B].

ScreenPixels = {flat_rgb}

Context: {reasoning_prompt}

What elements are visible? Respond with only structured insights (e.g., button names and coordinates if possible).
Avoid any hallucination. Be literal to the pixels.
"""

        try:
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", GEMINI_CLI, "--yolo"],
                input=prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )
            return result.stdout.strip()
        except Exception as e:
            return f"[Gemini CLI Error] {e}"

    @staticmethod
    def monitor_and_reason():
        """
        Continuously watch screen changes and invoke Gemini only when visual changes occur.
        """
        print("[PerceptionController] 👁️ Starting real-time visual loop...")
        while True:
            pixels, _ = PerceptionController.get_active_pixels()
            if PerceptionController.has_screen_changed(pixels):
                print("[PerceptionController] 🔄 Change detected. Sending to Gemini...")
                response = PerceptionController.ask_gemini_with_pixels(pixels)
                print("[Gemini 👁️] ", response)
            else:
                print("[PerceptionController] ⏸ No visual change.")
            time.sleep(0.2)

    @staticmethod
    def capture_screen_array():
        """
        Wrapper for PosterAgent & others.
        Simply returns a fresh raw RGB screen pixel array.
        """
        pixels, _ = PerceptionController.get_active_pixels()
        return pixels        