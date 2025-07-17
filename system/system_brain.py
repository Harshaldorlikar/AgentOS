# system/system_brain.py

import os
import json
import logging
from agents.agent_shell import AgentShell
from memory.memory import Memory
from system.agentos_core import AgentOSCore
from agents.supervisor import SupervisorAgent
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class SystemBrainAgent(AgentShell):
    """
    Reflects on agent logs to provide insights and summaries.
    This agent is a passive observer of the system's operation.
    """
    # --- FIX: Update __init__ to accept all shared components ---
    def __init__(self, core: AgentOSCore, memory: Memory, supervisor: SupervisorAgent, name="SystemBrain"):
        super().__init__(name=name, core=core, memory=memory, supervisor=supervisor)
        self.log_folder = "logs"
        self.task_context = "Review all agent logs for errors and insights."

    def run(self):
        """The main execution logic for the SystemBrainAgent."""
        self.log("Reviewing agent logs for insights...")
        thoughts = []

        if not os.path.exists(self.log_folder):
            self.log(f"Log folder '{self.log_folder}' not found. Nothing to review.", level="warning")
            return

        for filename in os.listdir(self.log_folder):
            if filename.endswith(".json"):
                path = os.path.join(self.log_folder, filename)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        for line in f:
                            try:
                                entry = json.loads(line)
                                # Check for log entries that are explicitly errors
                                if entry.get("level") == "error":
                                    thoughts.append(f"Found an error for agent '{entry.get('agent', 'unknown')}': {entry.get('message', 'No message')}")
                            except json.JSONDecodeError:
                                # This can happen if a log file is corrupted or partially written
                                self.log(f"Skipping malformed line in {filename}", level="warning")
                                continue
                except Exception as e:
                    self.log(f"Could not read log file {path}: {e}", level="error")
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "insights": thoughts or ["All systems nominal. No errors found in logs."]
        }
        
        # Use the shared memory instance to save the reflection
        self.memory.save("system_brain_reflection", summary)
        self.log(f"Reflection complete. Found {len(thoughts)} important insights.")

