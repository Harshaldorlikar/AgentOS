# tools/runtime_controller.py

import pyautogui
import subprocess
import webbrowser
import time
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_CLI = os.getenv("GEMINI_CLI")

class RuntimeController:
    @staticmethod
    def ask_gemini(prompt):
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
    def open_app(app_name, reason=None):
        if reason:
            prompt = f"""You're assisting an AI agent trying to open the app: "{app_name}".
Reason: "{reason}". If the app doesn't exist or takes too long to load, how should the agent respond?"""
            print("[Runtime AI] Gemini says:", RuntimeController.ask_gemini(prompt))
        subprocess.Popen(app_name)

    @staticmethod
    def browse(url, reason=None):
        if reason:
            prompt = f"""You're guiding an AI agent that needs to browse to: "{url}" to complete: "{reason}".
What should the agent do if the site doesn't load or asks for login?"""
            print("[Runtime AI] Gemini says:", RuntimeController.ask_gemini(prompt))
        webbrowser.open(url)

    @staticmethod
    def type_text(text, reason=None, delay=0.05):
        if reason:
            prompt = f"""The agent is typing: "{text}" for the task: "{reason}".
Assume the cursor is focused in the correct input field. What's the best way to type this efficiently and clearly?"""
            print("[Runtime AI] Gemini says:", RuntimeController.ask_gemini(prompt))

        for char in text:
            pyautogui.write(char)
            time.sleep(delay)

    @staticmethod
    def click(x, y, reason=None):
        if reason:
            prompt = f"""You're guiding an AI agent to click on screen coordinates ({x}, {y}) because: "{reason}".
What should it check visually before clicking to ensure it's correct and safe?"""
            print("[Runtime AI] Gemini says:", RuntimeController.ask_gemini(prompt))

        pyautogui.moveTo(x, y)
        pyautogui.click()

    @staticmethod
    def screenshot(path="screenshot.png", reason=None):
        if reason:
            prompt = f"""You're helping the agent capture a screenshot to: {path}.
Why might this be useful later, and how can screenshots help decision making?"""
            print("[Runtime AI] Gemini says:", RuntimeController.ask_gemini(prompt))

        pyautogui.screenshot(path)

    @staticmethod
    def perceive(window_title=None):
        from tools.perception_controller import PerceptionController
        return PerceptionController.get_perception_snapshot(window_title)

    @staticmethod
    def find_button_near(view, text_target):
        """
        Search OCR elements for a button with matching text. Returns its center coordinates.
        """
        elements = view.get("ui_elements", [])
        for el in elements:
            if text_target.lower() in el["text"].lower():
                x = el["left"] + el["width"] // 2
                y = el["top"] + el["height"] // 2
                return {"x": x, "y": y, "text": el["text"]}
        return None

    @staticmethod
    def find_textbox_near(view, placeholder_text):
        """
        Search OCR text boxes by matching a known label/placeholder like "What’s happening?"
        """
        elements = view.get("ui_elements", [])
        for el in elements:
            if placeholder_text.lower() in el["text"].lower():
                x = el["left"] + el["width"] // 2
                y = el["top"] + el["height"] // 2
                return {"x": x, "y": y, "text": el["text"]}
        return None
