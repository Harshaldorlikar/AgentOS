# agents/agent_launcher.py

import os
import json
import importlib
from agents.agent_shell import AgentShell
from agents.director_agent import DirectorAgent
from memory.memory import Memory

class AgentLauncher:
    def __init__(self, mission_file="missions/mission_001.json"):
        self.mission_file = mission_file
        self.memory = Memory()
        self.agents_map = self.load_agents_map()

    def launch_director(self):
        print("\nLaunching Director Agent...\n")
        director = DirectorAgent()
        director.run()

    def load_agents_map(self):
        """Load and import agent classes dynamically from agents_map.json"""
        agents_map = {}

        try:
            with open("agents_map.json", "r", encoding="utf-8") as f:
                raw_map = json.load(f)
        except FileNotFoundError:
            print("❌ agents_map.json not found.")
            return {}

        for name, path in raw_map.items():
            try:
                module = importlib.import_module(path)
                agent_class = getattr(module, name)
                agents_map[name] = agent_class
            except Exception as e:
                print(f"❌ Failed to import {name} from {path}: {e}")

        return agents_map

    def import_agent_class(self, agent_name):
        """Get agent class from loaded map"""
        return self.agents_map.get(agent_name)

    def load_mission(self):
        with open(self.mission_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_mission(self, mission):
        with open(self.mission_file, "w", encoding="utf-8") as f:
            json.dump(mission, f, indent=2)

    def launch_agents(self):
        mission = self.load_mission()
        updated_steps = []

        for step in mission["steps"]:
            agent_name = step["agent"]
            task = step["task"]

            AgentClass = self.import_agent_class(agent_name)
            if AgentClass is None:
                print(f"⚠️ No agent available for {agent_name}")
                step["status"] = "unavailable"
                updated_steps.append(step)
                continue

            agent = AgentClass(name=agent_name)
            agent.task_context = task

            step["status"] = "in_progress"
            self.save_mission(mission)

            try:
                print(f"🚀 Launching {agent_name} for task: {task}")
                agent.run()
                step["status"] = "completed"
            except Exception as e:
                print(f"❌ Error running {agent_name}: {e}")
                step["status"] = "error"
                step["error"] = str(e)

            updated_steps.append(step)

        mission["steps"] = updated_steps
        self.save_mission(mission)
