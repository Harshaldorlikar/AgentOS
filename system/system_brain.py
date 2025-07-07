# system/system_brain.py

import os
import json
from memory import memory
from datetime import datetime

class SystemBrainAgent:
    def __init__(self):
        self.name = "SystemBrain"
        self.memory = memory.Memory()
        self.log_folder = "logs"

    def reflect(self):
        print("SystemBrain is reviewing agent logs...")
        thoughts = []

        for file in os.listdir(self.log_folder):
            if file.endswith(".json"):
                path = os.path.join(self.log_folder, file)
                with open(path, "r") as f:
                    for line in f:
                        entry = json.loads(line)
                        if "error" in entry.get("message", "").lower():
                            thoughts.append(f"I found an error: {entry['message']}")

        summary = {
            "timestamp": datetime.now().isoformat(),
            "insights": thoughts or ["All systems nominal."]
        }

        self.memory.save("system_brain_reflection", summary)
        print("Reflection complete.")

    def run(self):
        self.reflect()
