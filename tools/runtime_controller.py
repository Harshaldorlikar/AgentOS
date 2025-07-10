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
    def open_app(app_name, reason=None):
        if reason:
            prompt = f"""You are helping an AI agent open the application: "{app_name}" to perform the task: "{reason}".
If the app is missing or slow to launch, how should the agent handle that?"""
            print("[Runtime AI] Gemini says:", RuntimeController.ask_gemini(prompt))
        subprocess.Popen(app_name)

    @staticmethod
    def browse(url, reason=None):
        if reason:
            prompt = f"""An AI agent needs to browse to: "{url}" to accomplish the task: "{reason}".
What should it do if the page fails to load or redirects to login?"""
            print("[Runtime AI] Gemini says:", RuntimeController.ask_gemini(prompt))
        webbrowser.open(url)

    @staticmethod
    def type_text(text, reason=None, delay=0.05, window_title=None):
        if reason:
            prompt = f"""You are helping an AI agent type the following content: "{text}" to complete: "{reason}".
What should the agent verify before typing?"""
            print("[Runtime AI] Gemini says:", RuntimeController.ask_gemini(prompt))
        if window_title:
            RuntimeController.focus_window_by_title(window_title)
        for char in text:
            pyautogui.write(char)
            time.sleep(delay)

    @staticmethod
    def click(x, y, reason=None, window_title=None):
        if reason:
            prompt = f"""You are helping an AI agent click on screen coordinates ({x}, {y}) to complete: "{reason}".
What should it double-check visually before proceeding?"""
            print("[Runtime AI] Gemini says:", RuntimeController.ask_gemini(prompt))
        if window_title:
            RuntimeController.focus_window_by_title(window_title)
        pyautogui.moveTo(x, y)
        pyautogui.click()

    @staticmethod
    def screenshot(path="screenshot.png", reason=None, window_title=None):
        if reason:
            prompt = f"""You are helping an AI agent capture a screenshot (saving to '{path}') to help with: "{reason}".
What details should be included and why?"""
            print("[Runtime AI] Gemini says:", RuntimeController.ask_gemini(prompt))
        if window_title:
            RuntimeController.focus_window_by_title(window_title)
        pyautogui.screenshot(path)

    @staticmethod
    def perceive(window_title=None):
        from tools.perception_controller import PerceptionController
        return PerceptionController.get_perception_snapshot(window_title)

    @staticmethod
    def find_button_near(text, perception_data, max_distance=100):
        from difflib import SequenceMatcher
        candidates = perception_data.get("ui_elements", [])
        target_text = text.lower()

        def score_match(t):
            return SequenceMatcher(None, t.lower(), target_text).ratio()

        # 🎯 Filter out buttons that are likely on the left sidebar (X.com layout)
        filtered_candidates = [el for el in candidates if el["left"] > 600]

        print("[RuntimeController] Filtering and scoring button matches...")
        matches = [
            (el, score_match(el["text"]))
            for el in filtered_candidates
            if len(el["text"].strip()) >= 2
        ]
        matches = sorted(matches, key=lambda x: -x[1])

        for el, score in matches:
            if score >= 0.85:
                print(f"[RuntimeController] 🎯 Match: '{el['text']}' with {score:.2f} at ({el['left']}, {el['top']})")
                x = el["left"] + el["width"] // 2
                y = el["top"] + el["height"] // 2
                return x, y, el["text"]

        print("[RuntimeController] ❌ No reliable match found for button.")
        return None, None, None