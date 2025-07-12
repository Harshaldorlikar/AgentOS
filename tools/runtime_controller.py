# tools/runtime_controller.py

import pyautogui
import subprocess
import webbrowser
import time
import os
from dotenv import load_dotenv
from tools.perception_controller import PerceptionController
load_dotenv()

GEMINI_CLI = os.getenv("GEMINI_CLI")

class RuntimeController:
    @staticmethod
    def ask_gemini_with_file(prompt_text):
        try:
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", GEMINI_CLI, "--yolo"],
                input=prompt_text,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )
            return result.stdout.strip()
        except Exception as e:
            return f"[Gemini CLI Error] {e}"

    @staticmethod
    def open_app(app_name, reason=None):
        if reason:
            print("[Runtime AI] Gemini says:", reason)
        subprocess.Popen(app_name)

    @staticmethod
    def browse(url, reason=None):
        if reason:
            print("[Runtime AI] Gemini says:", reason)
        webbrowser.open(url)

    @staticmethod
    def type_text(text, reason=None, delay=0.05, window_title=None):
        if reason:
            print("[Runtime AI] Gemini says:", reason)
        if window_title:
            RuntimeController.focus_window_by_title(window_title)
        for char in text:
            pyautogui.write(char)
            time.sleep(delay)

    @staticmethod
    def click(x, y, reason=None, window_title=None):
        if reason:
            print("[Runtime AI] Gemini says:", reason)
        if window_title:
            RuntimeController.focus_window_by_title(window_title)
        pyautogui.moveTo(x, y)
        pyautogui.click()

    @staticmethod
    def screenshot(path="screenshot.png", reason=None, window_title=None):
        if reason:
            print("[Runtime AI] Gemini says:", reason)
        pyautogui.screenshot(path)

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

    @staticmethod
    def perceive(force=False):
        """Triggers screen update and builds Gemini prompt"""
        if force:
            PerceptionController.force_capture()
        else:
            PerceptionController.update_if_changed()
        return PerceptionController.get_perception_snapshot()

    @staticmethod
    def analyze_screen_with_gemini(task="Identify UI buttons"):
        snapshot = RuntimeController.perceive(force=True)
        prompt = snapshot["prompt"]
        print("[RuntimeController] 🧠 Asking Gemini to analyze screen...")
        result = RuntimeController.ask_gemini_with_file(prompt)
        return result