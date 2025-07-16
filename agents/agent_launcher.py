# agents/agent_launcher.py
import sys
import os

# Add the root directory of AgentOS to PYTHONPATH
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import json
import importlib
import inspect
from memory.memory import Memory
from agents.supervisor import SupervisorAgent

class AgentLauncher:
    def __init__(self, mission_file="missions/mission_001.json"):
        self.mission_file = mission_file
        self.memory = Memory()
        self.supervisor = SupervisorAgent()
        self.agents_map = self.load_agents_map()

    def load_agents_map(self):
        path = "agents_map.json"
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ agents_map.json not found.")
            return {}

    def import_agent_class(self, agent_name):
        module_path = self.agents_map.get(agent_name)
        if not module_path:
            return None
        try:
            module = importlib.import_module(module_path)
            return getattr(module, agent_name)
        except Exception as e:
            print(f"❌ Failed to import {agent_name} from {module_path}: {e}")
            return None

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

            if not AgentClass:
                print(f"⚠️ No agent available for {agent_name}")
                step["status"] = "unavailable"
                updated_steps.append(step)
                continue

            try:
                # Inspect agent constructor to see what arguments it needs
                agent_args = inspect.signature(AgentClass.__init__).parameters

                if "name" in agent_args:
                    agent = AgentClass(name=agent_name)
                elif "memory" in agent_args and "supervisor" in agent_args:
                    agent = AgentClass(memory=self.memory, supervisor=self.supervisor)
                elif "memory" in agent_args:
                    agent = AgentClass(memory=self.memory)
                else:
                    agent = AgentClass()  # fallback

                agent.task_context = task
                step["status"] = "in_progress"
                self.save_mission(mission)

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