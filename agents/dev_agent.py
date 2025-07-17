# agents/dev_agent.py

import os
import subprocess
import json
import logging
from dotenv import load_dotenv
from agents.agent_shell import AgentShell
from memory.memory import Memory
from system.agentos_core import AgentOSCore
from agents.supervisor import SupervisorAgent

# Configure logging
logger = logging.getLogger(__name__)

class DevAgent(AgentShell):
    """
    A specialized agent that uses the Gemini CLI to generate Python code for
    new agents based on a user's high-level goal.
    """
    # --- FIX: Update __init__ to accept shared system components ---
    def __init__(self, core: AgentOSCore, memory: Memory, supervisor: SupervisorAgent, name="DevAgent"):
        super().__init__(name=name, core=core, memory=memory, supervisor=supervisor)
        self.task_context = "Use Gemini CLI to build new agents from a user goal"

    def _extract_agent_name(self, goal: str) -> str:
        """A simple utility to infer an agent's class name from a goal string."""
        # This can be replaced with a more sophisticated LLM call in the future
        goal = goal.lower()
        if "explorer" in goal: return "ExplorerAgent"
        if "writer" in goal: return "WriterAgent"
        if "poster" in goal: return "PosterAgent"
        if "director" in goal: return "DirectorAgent"
        if "patcher" in goal: return "SelfPatcherAgent"
        if "developer" in goal or "dev" in goal: return "DevAgent"
        return "AgentX" # A safe, neutral fallback name

    def _update_agent_map(self, agent_name: str):
        """Updates the agents_map.json file with the new agent's info."""
        path = "agents_map.json"
        agents_map = {}
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                agents_map = json.load(f)
        
        # The module path is derived from the agent name
        agents_map[agent_name] = f"agents.{agent_name.lower()}"
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(agents_map, f, indent=2)
        self.log(f"🗺️  agents_map.json updated for {agent_name}")

    def run(self):
        """The main execution logic for the DevAgent."""
        self.log("DevAgent is running.")
        
        mission = self.memory.load("mission_plan")
        if not mission:
            self.log("No mission plan found in memory. Nothing to do.", level="warning")
            return
            
        goal = mission.get("goal", "").strip()
        
        # Skip if the user didn't provide a specific goal for agent creation
        if not goal or goal.lower() in ["", "manual mission execution", "execute the predefined mission to write and post a tweet."]:
            self.log("No specific agent creation goal found. Skipping DevAgent execution.")
            return

        self.log(f"Found user goal for agent creation: '{goal}'")
        
        gemini_cli_path = os.getenv("GEMINI_CLI")
        if not gemini_cli_path:
            self.log("GEMINI_CLI path not found in .env file. Cannot generate code.", level="error")
            return

        context_file = "AGENTOS_CONTEXT.md"
        if not os.path.exists(context_file):
            self.log(f"{context_file} not found. Cannot provide context to model.", level="error")
            return

        with open(context_file, "r", encoding="utf-8") as f:
            context_prompt = f.read()

        agent_name_to_create = self._extract_agent_name(goal)
        
        full_prompt = f"""{context_prompt.strip()}

---

USER'S GOAL:
{goal}

---
Based on the context and the user's goal, generate the complete, production-ready Python code for the `{agent_name_to_create}` class.
The agent must inherit from AgentShell.
Only return the raw Python code. Do not add any explanation, comments, or markdown fences.
"""
        
        self.log(f"Generating code for {agent_name_to_create} via Gemini CLI...")
        try:
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", gemini_cli_path, "--yolo"],
                input=full_prompt, capture_output=True, text=True, encoding="utf-8", errors="ignore"
            )
            generated_code = result.stdout.strip()
        except Exception as e:
            self.log(f"Gemini CLI execution failed: {e}", level="error")
            return

        if not generated_code or "Traceback" in generated_code:
            self.log("Gemini output appears to be invalid or empty. Aborting.", level="error")
            return

        # Save the newly generated agent file
        filename = f"agents/{agent_name_to_create.lower()}.py"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(generated_code)
        self.log(f"✅ Agent file saved: {filename}")
        
        # Update the map so the launcher can find it
        self._update_agent_map(agent_name_to_create)
        self.log("DevAgent work is complete.")

