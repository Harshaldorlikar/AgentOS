# agents/supervisor_agent.py

import os
import subprocess
from datetime import datetime
import tempfile
from dotenv import load_dotenv
from PIL import Image
import numpy as np

load_dotenv()
GEMINI_CLI = os.getenv("GEMINI_CLI")

class SupervisorAgent:
    def __init__(self):
        self.logs = []
        self.last_perception = None  # For visual validation

    def approve_action(self, agent_name, action, value, task_context="", perception=None, bounding_box=None):
        """
        Main decision point for agent actions. Handles click safety, typing, and Gemini validation.
        """
        if perception:
            self.last_perception = perception
            print("[Supervisor] 👁️ Perception snapshot received.")

        # 🖱️ Click validation
        if action == "click":
            # Optional bounding box logic
            if bounding_box and perception:
                if self._validate_click_with_bounding_box(perception, bounding_box):
                    self.log_decision(agent_name, action, value, "Yes (bounding box match)")
                    return True

            # New: Gemini-based validation using pixel image
            if self._validate_click_with_gemini(value, perception, label_hint=task_context):
                self.log_decision(agent_name, action, value, "Yes (Gemini visual confirmation)")
                return True
            else:
                self.log_decision(agent_name, action, value, "No (Gemini rejected visual click)")
                return False

        # ✅ Safe defaults
        if action in ["open_browser", "open_app", "screenshot", "perceive"]:
            self.log_decision(agent_name, action, value, "Yes (safe default approval)")
            return True

        # ✍️ Typing
        if action == "type_text":
            if not value or len(value.strip()) < 5 or "???" in value:
                self.log_decision(agent_name, action, value, "No. Typing rejected (invalid content)")
                return False
            self.log_decision(agent_name, action, value, "Yes (validated for typing)")
            return True

        # 🧠 Fallback for complex tasks
        prompt = f"""
An AI agent named {agent_name} is running a task: "{task_context}".
It is about to perform this action: {action} → {value}.
Is this action necessary to complete the task?
Respond with one word: Yes or No. If no, briefly explain.
"""
        try:
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", GEMINI_CLI, "--yolo"],
                input=prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )
            response = result.stdout.strip()
        except Exception as e:
            response = f"No (Gemini CLI exception: {e})"

        approved = "yes" in response.lower()
        self.log_decision(agent_name, action, value, response)
        return approved

    def update_perception(self, snapshot: dict):
        self.last_perception = snapshot
        print("[Supervisor] 👁️ Updated perception stored.")

    def _validate_click_with_gemini(self, coords, perception, label_hint="Post"):
        """
        Sends screenshot to Gemini to ask: "Is it safe to click at (x, y)?"
        """
        try:
            pixel_array = perception.get("pixel_array")
            if pixel_array is None:
                print("[Supervisor] ❌ No pixel_array found for Gemini validation.")
                return False

            if isinstance(coords, str):
                x, y = map(int, coords.split(","))
            elif isinstance(coords, (list, tuple)) and len(coords) == 2:
                x, y = coords
            else:
                raise ValueError("Invalid coords format")

            # Save pixel array as image
            img = Image.fromarray(np.array(pixel_array).astype("uint8"), "RGB")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                img.save(tmp.name, format="PNG")
                image_path = tmp.name

            prompt = f"""
You are a safety validation agent.

Given this screenshot, is it visually correct to click at coordinates (x={x}, y={y}) if the intent is to click a '{label_hint}' button?

Only respond with:
Yes
or
No (with 5-word reason)
"""
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", GEMINI_CLI, "--yolo"],
                input=prompt + f"\n[FILE:{image_path}]",
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )
            response = result.stdout.strip()
            return "yes" in response.lower()
        except Exception as e:
            print(f"[Supervisor] ❌ Gemini click validation failed: {e}")
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

    def _validate_click_with_bounding_box(self, perception, box):
        for el in perception.get("ui_elements", []):
            if (
                el["text"].strip().lower() == box["text"].strip().lower() and
                abs(el["left"] + el["width"] // 2 - box["x"]) <= 10 and
                abs(el["top"] + el["height"] // 2 - box["y"]) <= 10
            ):
                print(f"[Supervisor] ✅ Exact bounding box match: {el['text']}")
                return True
        return False