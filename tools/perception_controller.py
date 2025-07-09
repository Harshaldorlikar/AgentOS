import pygetwindow as gw
import pyautogui
import pytesseract
from pywinauto import Application
from PIL import ImageGrab
import json

class PerceptionController:

    @staticmethod
    def get_active_window_title():
        window = gw.getActiveWindow()
        return window.title if window else "Unknown"

    @staticmethod
    def capture_screenshot():
        screenshot = pyautogui.screenshot()
        return screenshot

    @staticmethod
    def extract_text_ocr(image):
        text = pytesseract.image_to_string(image)
        return text.strip()

    @staticmethod
    def extract_ui_elements():
        elements = []
        try:
            app = Application(backend='uia').connect(active_only=True)
            window = app.top_window()
            for elem in window.descendants():
                try:
                    control_type = elem.friendly_class_name()
                    name = elem.window_text()
                    bounds = elem.rectangle
                    elements.append({
                        "type": control_type,
                        "name": name,
                        "coords": [bounds.left, bounds.top, bounds.right, bounds.bottom]
                    })
                except:
                    continue
        except Exception as e:
            elements.append({"error": str(e)})
        return elements

    @staticmethod
    def get_perception_snapshot():
        window_title = PerceptionController.get_active_window_title()
        screenshot = PerceptionController.capture_screenshot()
        ocr_text = PerceptionController.extract_text_ocr(screenshot)
        ui_elements = PerceptionController.extract_ui_elements()

        perception = {
            "active_window": window_title,
            "ocr_text": ocr_text,
            "ui_elements": ui_elements
        }

        return perception
