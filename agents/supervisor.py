# agents/supervisor_agent.py
import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv

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
        # Save perception if passed directly
        if perception:
            self.last_perception = perception
            print("[Supervisor] 👁️ Perception snapshot received.")

        # 🖱️ Click Validation using bounding box
        if action == "click":
            if bounding_box and perception:
                if self._validate_click_with_bounding_box(perception, bounding_box):
                    self.log_decision(agent_name, action, value, "Yes (bounding box match)")
                    return True
                else:
                    self.log_decision(agent_name, action, value, "No (bounding box mismatch)")
                    return False
            elif self._validate_click_with_perception(value):
                self.log_decision(agent_name, action, value, "Yes (fuzzy perception match)")
                return True
            elif "post" in task_context.lower():
                self.log_decision(agent_name, action, value, "Yes (context implies post click)")
                return True
            else:
                self.log_decision(agent_name, action, value, "No. Untrusted click.")
                return False

        # ✅ Auto-approve simple safe operations
        if action in ["open_browser", "open_app", "screenshot", "perceive"]:
            self.log_decision(agent_name, action, value, "Yes (safe default approval)")
            return True

        # ✍️ Typing safety
        if action == "type_text":
            if not value or len(value.strip()) < 5 or "???" in value:
                self.log_decision(agent_name, action, value, "No. Typing rejected (invalid content)")
                return False
            self.log_decision(agent_name, action, value, "Yes (validated for typing)")
            return True

        # 🤖 Gemini CLI fallback for complex/dangerous operations
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

    def update_perception(self, snapshot: dict):
        self.last_perception = snapshot
        print("[Supervisor] 👁️ Updated perception stored.")

    def _validate_click_with_perception(self, target):
        if not self.last_perception or "ui_elements" not in self.last_perception:
            return False
        try:
            x, y = self._parse_coords(target)
            for el in self.last_perception["ui_elements"]:
                if self._coord_in_element(x, y, el):
                    if "post" in el["text"].lower() or "tweet" in el["text"].lower():
                        print(f"[Supervisor] ✅ Fuzzy click validated near: '{el['text']}'")
                        return True
            print("[Supervisor] ❌ No matching 'post' element found.")
            return False
        except Exception as e:
            print(f"[Supervisor] ❌ Perception click validation failed: {e}")
            return False

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

    def _parse_coords(self, value):
        if isinstance(value, str) and "," in value:
            return map(int, value.split(","))
        elif isinstance(value, (list, tuple)) and len(value) == 2:
            return value
        raise ValueError("Invalid coordinate format")

    def _coord_in_element(self, x, y, el):
        return (
            el["left"] <= x <= el["left"] + el["width"] and
            el["top"] <= y <= el["top"] + el["height"]
        )