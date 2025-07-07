# agents/dev_agent.py

import os
import subprocess
import json
from agents.agent_shell import AgentShell
from memory.memory import Memory

class DevAgent(AgentShell):
    def __init__(self, name="DevAgent"):
        super().__init__(name=name)
        self.memory = Memory()

    def think(self):
        self.task_context = "Use Gemini CLI to build agents from user goal"
        self.mission = self.memory.load("mission_plan")
        self.goal = self.mission.get("goal", "Manual Mission Execution")
        self.log(f"Goal: {self.goal}")

def act(self):
    agent_name = self.extract_agent_name(self.goal)
    context_path = "AGENTOS_CONTEXT.md"

    # Load global AgentOS context
    try:
        with open(context_path, "r", encoding="utf-8") as f:
            context = f.read()
    except FileNotFoundError:
        self.log(f"❌ Context file not found: {context_path}")
        return

    # Load existing agent code if present
    existing_code = ""
    agent_path = f"agents/{agent_name.lower()}.py"
    if os.path.exists(agent_path):
        with open(agent_path, "r", encoding="utf-8") as f:
            existing_code = f.read()

    # Combine prompt
    prompt = f"""{context}

---

---

---

🧠 User's Goal:
{self.goal}

Now generate the full Python code for `{agent_name}`.
Only return code. Do not explain or print anything.
"""

        # Get CLI path from environment
    GEMINI_CLI = os.getenv("GEMINI_CLI")
    self.log(f"🔧 Gemini_CLI: {GEMINI_CLI}")
    if not GEMINI_CLI:
            self.log("❌ No GEMINI_CLI path found in .env.")
            return

    try:
            result = subprocess.run(
    ["powershell", "-ExecutionPolicy", "Bypass", "-File", GEMINI_CLI, "--yolo", "--all_files"],
    input=prompt,
    capture_output=True,
    text=True
)
            output = result.stdout.decode("utf-8", errors="ignore")
            output = result.stdout.strip()
    except Exception as e:
            self.log(f"❌ Gemini CLI failed: {e}")
            return

    if not output or "Traceback" in output:
            self.log("❌ Gemini output looks invalid or empty.")
            return

        # Validate constructor
    if "__init__" not in output or "name=" not in output:
            self.log("❌ Agent is missing a valid __init__(self, name=...) constructor.")
            return

        # Block dangerous code
    forbidden_keywords = ["requests", "openai", "urllib", "subprocess", "http", "google_web_search"]
    if any(kw in output for kw in forbidden_keywords):
            self.log("❌ Agent is trying to use forbidden libraries. Runtime Layer must be used instead.")
            return

        # Save the agent code
    filename = f"agents/{agent_name.lower()}.py"
    try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(output)
            self.log(f"📂 Detected agent file created: {filename}")
    except Exception as e:
            self.log(f"❌ Failed to save agent file: {e}")
            return

        # Update agents_map.json
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
        return "NewAgent"

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
