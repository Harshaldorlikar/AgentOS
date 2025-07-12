# tools/perception_controller.py
import time
import hashlib
import threading
from PIL import ImageGrab
import numpy as np
import google.generativeai as genai

class PerceptionController:
    last_hash = None
    last_frame = None
    last_result = None
    event_loop_running = False

    @classmethod
    def start_event_loop(cls, interval=0.2):
        if cls.event_loop_running:
            print("[Perception] 🔁 Already running.")
            return

        def loop():
            print("[Perception] 🎥 Starting event-driven perception loop...")
            cls.event_loop_running = True
            while cls.event_loop_running:
                cls.trigger_if_changed()
                time.sleep(interval)

        threading.Thread(target=loop, daemon=True).start()

    @classmethod
    def stop_event_loop(cls):
        cls.event_loop_running = False
        print("[Perception] 🛑 Event loop stopped.")

    @classmethod
    def get_latest_frame(cls):
        return cls.last_frame

    @classmethod
    def trigger_if_changed(cls):
        try:
            img = ImageGrab.grab()
            raw_bytes = img.tobytes()
            current_hash = hashlib.sha1(raw_bytes).hexdigest()

            if current_hash != cls.last_hash:
                cls.last_hash = current_hash
                cls.last_frame = img
                print("[Perception] 📸 Detected screen change. Calling Gemini...")
                cls.last_result = cls.send_to_gemini(img)
                print("[Perception] 🧠 Gemini Result:", cls.last_result)
            else:
                # print("[Perception] No change.")
                pass

        except Exception as e:
            print(f"[Perception] ❌ Error capturing screen: {e}")

    @classmethod
    def send_to_gemini(cls, image):
        try:
            model = genai.GenerativeModel("gemini-pro-vision")
            result = model.generate_content([
                "You are an AI agent monitoring a UI. What changed in the screen?",
                image
            ])
            return result.text
        except Exception as e:
            print(f"[Gemini] ❌ Error: {e}")
            return None