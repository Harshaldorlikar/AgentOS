# agents/agent_shell.py

import os
import json
import subprocess
import pyautogui
from datetime import datetime
from memory import memory
from agents.supervisor import SupervisorAgent

class AgentShell:
    def __init__(self, name="UnnamedAgent"):
        self.name = name
        self.task_context = "unknown"
        self.memory = memory.Memory()
        self.supervisor = SupervisorAgent()
        self.log_file = f"logs/{self.name.lower()}_log.json"
        os.makedirs("logs", exist_ok=True)

    def log(self, message):
        timestamp = datetime.now().isoformat()
        log_entry = {"timestamp": timestamp, "agent": self.name, "message": message}
        print(f"[{self.name}] {message}")
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def run(self):
        self.log("Agent started running.")
        self.think()
        self.act()
        self.log("Agent finished execution.")

    # === Hooks to override ===
    def think(self):
        self.log("Thinking... (override in child class)")

    def act(self):
        self.log("Acting... (override in child class)")

    # === PC Control Utilities ===

    def open_app(self, path):
        if self.supervisor.approve_action(self.name, "open_app", path, self.task_context):
            try:
                subprocess.Popen(path)
                self.log(f"Opened app: {path}")
            except Exception as e:
                self.log(f"Failed to open app: {e}")
        else:
            self.log(f"Supervisor blocked opening: {path}")

    def type_text(self, text, interval=0.05):
        if self.supervisor.approve_action(self.name, "type_text", text, self.task_context):
            pyautogui.write(text, interval=interval)
            self.log(f"Typed: {text}")
        else:
            self.log("Supervisor blocked typing.")

    def press_key(self, key):
        if self.supervisor.approve_action(self.name, "press_key", key, self.task_context):
            pyautogui.press(key)
            self.log(f"Pressed key: {key}")
        else:
            self.log("Supervisor blocked keypress.")

    def move_mouse(self, x, y):
        if self.supervisor.approve_action(self.name, "move_mouse", f"{x}, {y}", self.task_context):
            pyautogui.moveTo(x, y, duration=0.5)
            self.log(f"Moved mouse to: {x}, {y}")
        else:
            self.log("Supervisor blocked mouse move.")

    def click_mouse(self):
        if self.supervisor.approve_action(self.name, "click_mouse", "left", self.task_context):
            pyautogui.click()
            self.log("Mouse clicked.")
        else:
            self.log("Supervisor blocked mouse click.")

    def take_screenshot(self, filename="screenshot.png"):
        path = os.path.join("logs", filename)
        pyautogui.screenshot(path)
        self.log(f"Saved screenshot to {path}")
