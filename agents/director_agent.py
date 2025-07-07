# agents/director_agent.py

import os
import json
from agents.agent_shell import AgentShell
from memory.memory import Memory

class DirectorAgent(AgentShell):
    def __init__(self, name="DirectorAgent"):
        super().__init__(name=name)
        self.memory = Memory()
        self.user_goal = None

    def think(self):
        print("🧠 What do you want the agents to do?")
        print(" - Type a prompt to generate an agent")
        print(" - Or just press [Enter] to skip and continue with existing mission\n")

        user_input = input("> ").strip()

        if not user_input:
            self.log("✅ Skipping agent creation. Proceeding with existing mission.")
            self.user_goal = None
            return

        self.user_goal = user_input
        self.log(f"🧠 User wants: {self.user_goal}")
        self.log("📋 Creating mission plan...")

        mission = {
            "goal": self.user_goal,
            "steps": [
                {
                    "agent": "WriterAgent",
                    "task": "Write a motivational tweet using trending topics",
                    "status": "pending"
                },
                {
                    "agent": "PosterAgent",
                    "task": "Post content to X (Twitter)",
                    "status": "pending"
                }
            ]
        }

        os.makedirs("missions", exist_ok=True)
        with open("missions/mission_001.json", "w", encoding="utf-8") as f:
            json.dump(mission, f, indent=2)

        self.memory.save("mission_plan", mission)
        self.log("📋 Mission plan saved. Passing to DevAgent next.")

    def act(self):
        if not self.user_goal:
            self.log("⚠️ No user goal provided. Skipping mission planning.")
            return
        self.log("🎯 Acting... (this is typically overridden)")
