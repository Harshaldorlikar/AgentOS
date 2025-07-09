import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
GEMINI_CLI = os.getenv("GEMINI_CLI")

class SupervisorAgent:
    def __init__(self):
        self.logs = []

    def approve_action(self, agent_name, action, value, task_context=""):
        # Special check for clicking: only allow if clearly needed
        if action == "click_mouse":
            if "post" in task_context.lower() or "submit" in task_context.lower():
                self.log_decision(agent_name, action, value, "Yes (validated for posting)")
                return True
            else:
                self.log_decision(agent_name, action, value, "No. Click request must include reason like 'Post the tweet'.")
                return False

        # Normal Gemini CLI-based validation
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
