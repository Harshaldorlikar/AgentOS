# agents/supervisor.py

import os
import tempfile
import json
from datetime import datetime
import numpy as np
from PIL import Image
from dotenv import load_dotenv

from tools.gemini_model_api import smart_vision_query  # ✅ Replaces ask_gemini_with_file
from tools.debug_visualizer import draw_button_overlay
from tools.gemini_ui_vision import analyze_ui_elements_from_pixels
from memory.memory import Memory

load_dotenv()

def strip_code_wrappers(text):
    if text.strip().startswith("```"):
        lines = text.strip().splitlines()
        return "\n".join(line for line in lines if not line.strip().startswith("```"))
    return text.strip()

class SupervisorAgent:
    def __init__(self):
        self.logs = []
        self.last_perception = None
        self.memory = Memory()

    def update_perception(self, snapshot: dict):
        self.last_perception = snapshot
        print("[Supervisor] 👁️ Updated perception stored.")

    def approve_action(self, agent_name, action, value, task_context="", perception=None, bounding_box=None):
        if perception:
            self.last_perception = perception
            print("[Supervisor] 👁️ Perception snapshot received.")

        if action == "click":
            label_hint = bounding_box.get("text") if bounding_box else task_context or "button"

            if bounding_box and perception:
                if self._is_click_inside_bounding_box(value, bounding_box):
                    print("[Supervisor] ✅ Click falls within bounding box.")
                    self.log_decision(agent_name, action, value, "Yes (bounding box match)")
                    return True

            success, reason = self._validate_click_with_gemini(value, perception, label_hint)
            if success:
                self.log_decision(agent_name, action, value, "Yes (Gemini visual confirmation)")
                return True
            else:
                self.log_decision(agent_name, action, value, f"No (Gemini rejected: {reason})")
                return False

        elif action == "type_text":
            if not value or len(value.strip()) < 5 or "???" in value:
                self.log_decision(agent_name, action, value, "No. Typing rejected (invalid content)")
                return False
            self.log_decision(agent_name, action, value, "Yes (validated for typing)")
            return True

        elif action in ["open_browser", "open_app", "screenshot", "perceive"]:
            self.log_decision(agent_name, action, value, "Yes (safe default approval)")
            return True

        # Default fallback: ask Gemini text-only (no image)
        prompt = f"""
An AI agent named {agent_name} is running a task: "{task_context}".
It is about to perform this action: {action} → {value}.
Is this action necessary to complete the task?
Respond with one word: Yes or No. If no, briefly explain.
"""
        try:
            response = smart_vision_query(prompt, None)
        except Exception as e:
            response = f"No (Gemini exception: {e})"

        approved = "yes" in response.lower()
        self.log_decision(agent_name, action, value, response)
        return approved

    def analyze_ui(self, task_prompt):
        print(f"[Supervisor] 🧠 Analyzing UI for task: {task_prompt}")
        if not self.last_perception or "pixel_array" not in self.last_perception:
            print("[Supervisor] ❌ No perception available.")
            return []

        pixel_array = self.last_perception["pixel_array"]
        try:
            parsed = analyze_ui_elements_from_pixels(pixel_array, task_prompt)
            self.last_perception["ui_elements"] = parsed
            return parsed
        except Exception as e:
            print(f"[Supervisor] ❌ Failed to analyze UI: {e}")
            return []

    def _validate_click_with_gemini(self, coords, perception, label_hint="Post"):
        try:
            pixel_array = perception.get("pixel_array")
            if pixel_array is None:
                return False, "No pixel_array found"

            if isinstance(coords, str):
                x, y = map(int, coords.split(","))
            elif isinstance(coords, (list, tuple)) and len(coords) == 2:
                x, y = coords
            else:
                return False, "Invalid coords format"

            img = Image.fromarray(np.array(pixel_array).astype("uint8"), "RGB")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                img.save(tmp.name, format="PNG")
                image_path = tmp.name

            prompt = f"""
You are a visual UI agent validating a click on a button labeled '{label_hint}'.
Only approve if the coordinates (x={x}, y={y}) fall clearly inside the correct button (e.g. Post or Send).
Is it safe to click at these coordinates?
Respond strictly with:
Yes
or
No (with a short reason)
"""

            response = smart_vision_query(prompt, image_path)  # ✅ Uses model fallback
            if "yes" in response.lower():
                print(f"[Supervisor] ✅ Gemini approved click at ({x},{y}) for '{label_hint}'.")
                return True, "Approved"
            else:
                print(f"[Supervisor] ❌ Gemini rejected click at ({x},{y}) for '{label_hint}': {response}")
                return False, response

        except Exception as e:
            return False, f"Gemini click validation error: {e}"

    def _is_click_inside_bounding_box(self, coords, box):
        try:
            if isinstance(coords, str):
                x, y = map(int, coords.split(","))
            elif isinstance(coords, (list, tuple)):
                x, y = coords
            else:
                return False
            return box["x_min"] <= x <= box["x_max"] and box["y_min"] <= y <= box["y_max"]
        except:
            return False

    def log_decision(self, agent_name, action, value, response):
        status = "approved" if "yes" in response.lower() else "blocked"
        decision = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "action": action,
            "value": value,
            "response": response,
            "status": status
        }
        self.logs.append(decision)
        print(f"[Supervisor] {action} → {status}: {response}")
