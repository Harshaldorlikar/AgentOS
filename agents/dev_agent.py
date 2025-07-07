# agents/dev_agent.py

import os
import subprocess
import json
from dotenv import load_dotenv
from agents.agent_shell import AgentShell
from memory.memory import Memory

class DevAgent(AgentShell):
    def __init__(self, name="DevAgent"):
        super().__init__(name=name)
        self.memory = Memory()

    def think(self):
        self.task_context = "Use Gemini CLI to build agents from user goal"
        self.mission = self.memory.load("mission_plan")
        self.goal = self.mission.get("goal", "").strip()
        self.log(f"Goal: {self.goal}")

    def act(self):
        load_dotenv()
        gemini_cli = os.getenv("GEMINI_CLI")
        if not gemini_cli:
            self.log("❌ GEMINI_CLI path not found in .env.")
            return

        # Abort if user skipped or gave no meaningful goal
        if not self.goal or self.goal.lower() in ["", "manual mission execution", "skip", "none"]:
            self.log("⚠️ No valid goal found. Skipping DevAgent.")
            return

        self.log(f"🔧 Gemini_CLI: {gemini_cli}")

        agent_name = self.extract_agent_name(self.goal)

        # Load project context
        context_file = "agentos_context.md"
        if not os.path.exists(context_file):
            self.log(f"❌ {context_file} not found.")
            return

        with open(context_file, "r", encoding="utf-8") as f:
            context = f.read()

        # Build prompt
        prompt = f"""{context.strip()}

---

🧠 User's Goal:
{self.goal}

Now generate the full Python code for `{agent_name}`.
Only return code. Do not explain or print anything.
"""

        try:
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", gemini_cli, "--yolo"],
                input=prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )
            output = result.stdout.strip()
        except Exception as e:
            self.log(f"❌ Gemini CLI failed: {e}")
            return

        if not output or "Traceback" in output:
            self.log("❌ Gemini output looks invalid or empty.")
            return

        if "__init__" not in output or "name=" not in output:
            self.log("❌ Agent is missing a valid __init__(self, name=...) constructor.")
            return

        forbidden_keywords = ["requests", "openai", "urllib", "subprocess", "http", "google_web_search"]
        if any(kw in output for kw in forbidden_keywords):
            self.log("❌ Agent is trying to use forbidden libraries. Runtime Layer must be used instead.")
            return

        # Save agent file
        filename = f"agents/{agent_name.lower()}.py"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(output)
            self.log(f"📂 Agent file saved: {filename}")
        except Exception as e:
            self.log(f"❌ Failed to save agent file: {e}")
            return

        # Update map
        self.update_agent_map(agent_name)
        self.log(f"🧠 {agent_name} added to agents_map.json")
        self.log(f"✅ Agent created: {agent_name}")

    def extract_agent_name(self, goal):
        goal = goal.lower()
        if "explorer" in goal:
            return "ExplorerAgent"
        elif "writer" in goal:
            return "WriterAgent"
        elif "poster" in goal:
            return "PosterAgent"
        elif "director" in goal:
            return "DirectorAgent"
        elif "patcher" in goal:
            return "SelfPatcherAgent"
        elif "developer" in goal:
            return "DevAgent"
        return "AgentX"  # No fallback to NewAgent — return safe neutral name

    def update_agent_map(self, agent_name):
        path = "agents_map.json"
        agents_map = {}

        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                agents_map = json.load(f)

        agents_map[agent_name] = f"agents.{agent_name.lower()}"

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(agents_map, f, indent=2)
        except Exception as e:
            self.log(f"❌ Failed to update agents_map.json: {e}")
