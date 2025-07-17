# system/self_patcher.py

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

class SelfPatcherAgent(AgentShell):
    """
    A system-level agent that scans logs for errors and suggests
    corrective actions or 'patches'.
    """
    # --- FIX: Update __init__ to accept all shared components ---
    def __init__(self, core: AgentOSCore, memory: Memory, supervisor: SupervisorAgent, name="SelfPatcher"):
        super().__init__(name=name, core=core, memory=memory, supervisor=supervisor)
        self.log_folder = "logs"
        self.task_context = "Scan system logs for errors and suggest patches."

    def _scan_logs_for_failures(self) -> list[str]:
        """Scans all .json log files for entries with a level of 'error'."""
        self.log("Scanning logs for failure signatures...")
        actions_needed = []

        if not os.path.exists(self.log_folder):
            self.log(f"Log folder '{self.log_folder}' not found. Nothing to scan.", level="warning")
            return []

        for filename in os.listdir(self.log_folder):
            if filename.endswith(".json"):
                path = os.path.join(self.log_folder, filename)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        for line in f:
                            try:
                                entry = json.loads(line)
                                if entry.get("level") == "error":
                                    error_message = f"Restart agent '{entry.get('agent', 'unknown')}' due to error: {entry.get('message', 'No message')}"
                                    actions_needed.append(error_message)
                            except json.JSONDecodeError:
                                continue # Skip malformed log lines
                except Exception as e:
                    self.log(f"Could not read log file {path}: {e}", level="error")
        
        return actions_needed

    def run(self):
        """The main execution logic for the SelfPatcherAgent."""
        actions = self._scan_logs_for_failures()

        if not actions:
            self.log("Scan complete. No patching actions needed.")
            return

        patch_plan = {
            "timestamp": datetime.now().isoformat(),
            "suggested_actions": actions
        }

        # Use the shared memory instance to save the suggestions
        self.memory.save("self_patcher_suggestions", patch_plan)
        self.log(f"Scan complete. Found {len(actions)} potential issues and saved patch plan to memory.")
