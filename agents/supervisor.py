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
        prompt = f"""
An AI agent named {agent_name} is running a task: "{task_context}".
It is about to perform this action: {action} → {value}.

Is this action necessary to complete the task?
Respond with one word: Yes or No. If no, briefly explain.
"""

        try:
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", GEMINI_CLI, prompt],
                capture_output=True,
                text=True
            )
            response = result.stdout.strip()
        except Exception as e:
            response = f"No (Gemini CLI exception: {e})"

        decision = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "action": action,
            "value": value,
            "response": response
        }

        approved = "yes" in response.lower()
        status = "approved" if approved else "blocked"
        decision["status"] = status
        self.logs.append(decision)

        print(f"[Supervisor] {action} → {status}: {response}")
        return approved
