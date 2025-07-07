# agents/supervisor.py

import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# Load CLI path from .env
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
Reply with only one word: Yes or No. If No, briefly explain why.
"""

        if not GEMINI_CLI or not os.path.exists(GEMINI_CLI):
            print("[Supervisor] ❌ GEMINI_CLI not found or invalid.")
            return False

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
            response = f"No (Gemini CLI error: {e})"

        # Decision Logging
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
