# system/self_patcher.py

import os
import json
from memory import memory
from datetime import datetime

class SelfPatcherAgent:
    def __init__(self):
        self.name = "SelfPatcher"
        self.memory = memory.Memory()
        self.log_folder = "logs"

    def scan_for_failures(self):
        print("SelfPatcher is scanning logs for failures...")
        actions_needed = []

        for file in os.listdir(self.log_folder):
            if file.endswith(".json"):
                path = os.path.join(self.log_folder, file)
                with open(path, "r") as f:
                    for line in f:
                        entry = json.loads(line)
                        if "error" in entry.get("message", "").lower():
                            actions_needed.append(f"Restart {entry['agent']} due to error: {entry['message']}")

        if not actions_needed:
            actions_needed.append("No patching needed.")

        patch_plan = {
            "timestamp": datetime.now().isoformat(),
            "actions": actions_needed
        }

        self.memory.save("self_patcher_suggestions", patch_plan)
        print("Scan complete.")

    def run(self):
        self.scan_for_failures()
