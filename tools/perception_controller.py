# tools/perception_controller.py

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
            return f"Error getting active window: {e}"

    @staticmethod
    def focus_and_screenshot_window(window_title_keywords):
        try:
            # Match by partial keyword in title (case-insensitive)
            all_windows = gw.getAllTitles()
            matching_titles = [title for title in all_windows if window_title_keywords.lower() in title.lower()]
            if not matching_titles:
                print(f"[Perception] ❌ No window found with title containing: {window_title_keywords}")
                return None, "Window not found"

            windows = gw.getWindowsWithTitle(matching_titles[0])
            if not windows:
                print(f"[Perception] ❌ Window not available: {matching_titles[0]}")
                return None, "Window not available"

            target_window = windows[0]
            if not target_window.isActive:
                target_window.activate()
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
            print(f"[Perception] ❌ Error focusing/screenshotting window: {e}")
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
    def get_perception_snapshot(target_window_keyword=""):
        if target_window_keyword:
            screenshot, window_title = PerceptionController.focus_and_screenshot_window(target_window_keyword)
        else:
            screenshot = pyautogui.screenshot()
            window_title = PerceptionController.get_active_window_title()

        if screenshot is None:
            return {
                "active_window": window_title,
                "ocr_text": "❌ Screenshot failed",
                "ui_elements": []
            }

        text_elements = PerceptionController.extract_text_elements(screenshot)

        return {
            "active_window": window_title,
            "ocr_text": " ".join([el["text"] for el in text_elements]),
            "ui_elements": text_elements
        }
