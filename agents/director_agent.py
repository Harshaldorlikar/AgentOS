# agents/director_agent.py

import os
import json
import logging
from agents.agent_shell import AgentShell
from memory.memory import Memory
from system.agentos_core import AgentOSCore
from agents.supervisor import SupervisorAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DirectorAgent(AgentShell):
    """
    The initial agent that interacts with the user to define the mission's goal
    and builds the mission plan for other agents to execute.
    """
    # --- FIX: Update __init__ to accept shared system components ---
    def __init__(self, core: AgentOSCore, memory: Memory, supervisor: SupervisorAgent, name="DirectorAgent"):
        # The 'name' is now passed to the shell's constructor
        super().__init__(name=name, core=core, memory=memory, supervisor=supervisor)
        self.user_goal = None

    def _build_mission(self, goal: str):
        """Creates and saves the mission JSON file."""
        mission = {
            "goal": goal,
            "steps": [
                # This can be made more dynamic in the future, but for now, it's a set plan.
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

        try:
            # Ensure the missions directory exists
            os.makedirs("missions", exist_ok=True)
            with open("missions/mission_001.json", "w", encoding="utf-8") as f:
                json.dump(mission, f, indent=2)
            
            # Use the shared memory instance to save the plan
            self.memory.save("mission_plan", mission)
            self.log("📋 Mission plan created and saved successfully.")
        except Exception as e:
            self.log(f"❌ Failed to save mission file: {e}", level="error")

    def run(self):
        """
        The main execution logic for the DirectorAgent. Replaces think() and act().
        """
        self.log("Director Agent is running. Awaiting user input for the mission goal.")
        print("\n--- [Mission Director] ---")
        print("🧠 What is the high-level goal for the agent team?")
        print("   (e.g., 'Write and post a funny tweet about AI')")
        print("   (Press [Enter] to skip and use the default mission)")
        
        user_input = input("> ").strip()

        if not user_input:
            self.log("✅ No user goal provided. Proceeding with the default mission plan.")
            self.user_goal = "Execute the predefined mission to write and post a tweet."
        else:
            self.user_goal = user_input
            self.log(f"🧠 User goal received: {self.user_goal}")

        # Build the mission file based on the goal.
        self._build_mission(self.user_goal)
        self.log("Director's work is complete. Handing off to the launcher.")

