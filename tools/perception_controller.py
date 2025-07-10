import pygetwindow as gw
import pyautogui
import pytesseract
from PIL import ImageGrab
import numpy as np
import time

class PerceptionController:
    @staticmethod
    def get_active_window_title():
        try:
            active_window = gw.getActiveWindow()
            return active_window.title if active_window else "Unknown"
        except Exception as e:
            return f"[Perception] ❌ Error getting active window: {e}"

    @staticmethod
    def find_window_by_keywords(keywords):
        try:
            windows = gw.getAllTitles()
            for win_title in windows:
                if all(kw.lower() in win_title.lower() for kw in keywords):
                    return gw.getWindowsWithTitle(win_title)[0]
        except Exception as e:
            print(f"[Perception] ❌ Window search error: {e}")
        return None

    @staticmethod
    def focus_and_capture_window(window_keywords):
        try:
            target_window = PerceptionController.find_window_by_keywords(window_keywords)
            if not target_window:
                print(f"[Perception] ❌ No window found with keywords: {window_keywords}")
                return None, "Window not found"

            if not target_window.isActive:
                target_window.activate()
                time.sleep(1)

            if not target_window.isMaximized:
                target_window.maximize()
                time.sleep(1)

            bbox = (
                target_window.left,
                target_window.top,
                target_window.left + target_window.width,
                target_window.top + target_window.height
            )

            screenshot = ImageGrab.grab(bbox=bbox)
            return screenshot, target_window.title
        except Exception as e:
            print(f"[Perception] ❌ Error capturing window: {e}")
            return None, str(e)

    @staticmethod
    def extract_text_elements(image):
        try:
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            elements = []
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 60 and data['text'][i].strip():
                    elements.append({
                        "text": data['text'][i],
                        "left": data['left'][i],
                        "top": data['top'][i],
                        "width": data['width'][i],
                        "height": data['height'][i]
                    })
            return elements
        except Exception as e:
            print(f"[Perception] ❌ OCR failed: {e}")
            return []

    @staticmethod
    def get_perception_snapshot(window_keywords=""):
        if window_keywords:
            screenshot, window_title = PerceptionController.focus_and_capture_window(window_keywords.split())
        else:
            screenshot = pyautogui.screenshot()
            window_title = PerceptionController.get_active_window_title()

        if screenshot is None:
            return {
                "active_window": window_title,
                "ocr_text": "❌ Screenshot failed",
                "ui_elements": []
            }

        elements = PerceptionController.extract_text_elements(screenshot)
        return {
            "active_window": window_title,
            "ocr_text": " ".join([el["text"] for el in elements]),
            "ui_elements": elements
        }