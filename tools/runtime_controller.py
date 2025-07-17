# tools/runtime_controller.py

import os
import pyautogui
import subprocess
import webbrowser
import time
from dotenv import load_dotenv

load_dotenv()

# DPI-aware settings for high-DPI screens
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

class RuntimeController:
    """
    This is the 'hands' of AgentOS.
    Executes actions in the OS (click, type, open app) based on agent commands.
    """

    @staticmethod
    def open_app(app_path, reason=None):
        if reason:
            print(f"[RuntimeController] 🧠 Reason: {reason}")
        try:
            subprocess.Popen(app_path)
        except Exception as e:
            print(f"[RuntimeController] ❌ Failed to open {app_path}: {e}")

    @staticmethod
    def browse(url, reason=None):
        if reason:
            print(f"[RuntimeController] 🌐 Reason: {reason}")
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"[RuntimeController] ❌ Failed to open browser: {e}")

    @staticmethod
    def type_text(text, reason=None, delay=0.05, window_title=None):
        if reason:
            print(f"[RuntimeController] ⌨️ Reason: {reason}")
        if window_title:
            RuntimeController.focus_window_by_title(window_title)
        for char in text:
            pyautogui.write(char)
            time.sleep(delay)

    @staticmethod
    def click(x, y, reason=None, window_title=None):
        if reason:
            print(f"[RuntimeController] 🖱️ Reason: {reason}")
        if window_title:
            RuntimeController.focus_window_by_title(window_title)

        # Convert to DPI-safe coordinates (auto-adjust if needed)
        scale_x, scale_y = pyautogui.size()
        x = min(max(x, 0), scale_x - 1)
        y = min(max(y, 0), scale_y - 1)

        try:
            pyautogui.moveTo(x, y)
            pyautogui.click()
        except Exception as e:
            print(f"[RuntimeController] ❌ Click failed at ({x},{y}): {e}")

    @staticmethod
    def focus_window_by_title(title_keywords):
        try:
            import pygetwindow as gw
            windows = gw.getWindowsWithTitle(title_keywords)
            if windows:
                win = windows[0]
                if not win.isActive:
                    win.activate()
                    time.sleep(1)
        except Exception as e:
            print(f"[RuntimeController] ❌ Window focus failed: {e}")
