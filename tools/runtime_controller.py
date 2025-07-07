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
                encoding="utf-8",  # ✅ Fixes UnicodeDecodeError
                errors="ignore"    # ✅ Avoids breaking on emojis like 🧠
)

            return result.stdout.strip()
        except Exception as e:
            return f"[Gemini CLI Error] {e}"

    @staticmethod
    def open_app(app_name, reason=None):
        if "chrome" in app_name.lower():
            chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            user_data = r'--profile-directory="Harshal Main Profile"'
            app = f'{chrome_path} {user_data}'
        else:
            app = app_name

        if reason:
            prompt = f"""You are an AI agent asked to open the app: "{app}" for reason: "{reason}".
    Explain how this contributes to the user's goal."""
            print("[Runtime AI] Gemini says:", RuntimeController.ask_gemini(prompt))

        subprocess.Popen(app)

    @staticmethod
    def browse(url, reason=None):
        if reason:
            prompt = f"""You need to browse to the URL: "{url}" to complete the task: "{reason}".
Make sure it's correct. Suggest actions if page fails to load."""
            print("[Runtime AI] Gemini says:", RuntimeController.ask_gemini(prompt))

        webbrowser.open(url)

    @staticmethod
    def type_text(text, reason=None, delay=0.05):
        if reason:
            prompt = f"""You are typing the following content: "{text}" for reason: "{reason}".
Where should you type it? Assume the user has opened the correct input box."""
            print("[Runtime AI] Gemini says:", RuntimeController.ask_gemini(prompt))

        for char in text:
            pyautogui.write(char)
            time.sleep(delay)

    @staticmethod
    def click(x, y, reason=None):
        if reason:
            prompt = f"""You are going to click on coordinates ({x}, {y}) because: {reason}.
What should you check before clicking?"""
            print("[Runtime AI] Gemini says:", RuntimeController.ask_gemini(prompt))

        pyautogui.moveTo(x, y)
        pyautogui.click()

    @staticmethod
    def screenshot(path="screenshot.png", reason=None):
        if reason:
            prompt = f"""You need to take a screenshot and save it to '{path}' because: {reason}.
What can you do with this screenshot later?"""
            print("[Runtime AI] Gemini says:", RuntimeController.ask_gemini(prompt))

        pyautogui.screenshot(path)
