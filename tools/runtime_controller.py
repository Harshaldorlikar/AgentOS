# tools/runtime_controller.py

import pyautogui
import webbrowser
import time
import logging
import subprocess

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure PyAutoGUI for safety and reliability
pyautogui.FAILSAFE = True  # Allows you to abort by moving the mouse to the top-left corner
pyautogui.PAUSE = 0.1      # A small pause after each action

class RuntimeController:
    """
    This is the 'hands' of AgentOS. It is a pure action-taker that executes
    low-level OS commands like mouse clicks and keyboard input as directed by the AgentOSCore.
    """

    @staticmethod
    def open_app(app_path: str, reason: str = None):
        """
        Opens a desktop application from a given path.
        Note: Use with caution as this can be a security risk without sandboxing.
        """
        if reason:
            print(f"[RuntimeController] 🚀 Reason: {reason}")
        try:
            subprocess.Popen(app_path)
            logger.info(f"Opened application: {app_path}")
        except Exception as e:
            logger.error(f"Failed to open application {app_path}: {e}", exc_info=True)

    @staticmethod
    def browse(url: str, reason: str = None):
        """Opens a URL in the default web browser."""
        if reason:
            print(f"[RuntimeController] 🌐 Reason: {reason}")
        try:
            webbrowser.open(url)
            logger.info(f"Opened URL: {url}")
        except Exception as e:
            logger.error(f"Failed to open URL {url}: {e}", exc_info=True)

    @staticmethod
    def type_text(text: str, reason: str = None, delay: float = 0.05):
        """
        Types the given text with a small delay between characters for reliability.
        """
        if reason:
            print(f"[RuntimeController] ⌨️ Reason: {reason}")
        try:
            # A short pause before typing can help ensure the correct window is focused
            time.sleep(0.5)
            pyautogui.write(text, interval=delay)
            logger.info(f"Typed {len(text)} characters.")
        except Exception as e:
            logger.error(f"Failed to type text: {e}", exc_info=True)

    @staticmethod
    def click(x: int, y: int, reason: str = None):
        """
        Moves the mouse to the specified logical coordinates and performs a click.
        Includes boundary checks to prevent errors.
        """
        if reason:
            print(f"[RuntimeController] 🖱️ Reason: {reason}")
        try:
            # Get the primary screen's dimensions for boundary checking
            screen_width, screen_height = pyautogui.size()
            
            # Clamp coordinates to be within the screen bounds
            safe_x = max(0, min(x, screen_width - 1))
            safe_y = max(0, min(y, screen_height - 1))

            if x != safe_x or y != safe_y:
                logger.warning(f"Original click coordinates ({x}, {y}) were out of bounds. Clamped to ({safe_x}, {safe_y}).")

            # A short move duration is more human-like and can be more reliable
            pyautogui.moveTo(safe_x, safe_y, duration=0.25)
            pyautogui.click()
            logger.info(f"Clicked at logical coordinates: ({safe_x}, {safe_y})")
        except Exception as e:
            logger.error(f"Failed to click at ({x}, {y}): {e}", exc_info=True)

