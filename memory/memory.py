# memory/memory.py

import json
import os

MEMORY_FILE = "memory/memory.json"

class Memory:
    def __init__(self):
        os.makedirs("memory", exist_ok=True)
        if not os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "w") as f:
                json.dump({}, f)

    def save(self, key, value):
        data = self.load_all()
        data[key] = value
        with open(MEMORY_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def load(self, key):
        data = self.load_all()
        return data.get(key)

    def load_all(self):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
