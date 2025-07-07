# 🧠 AgentOS — The AI-Native Operating System for Autonomous Agent Teams

**AgentOS** is a modular operating system that allows intelligent agents to operate computers like humans — using apps, browsing, typing, clicking, learning, and even evolving.
  Built for running agentic AI organizations, AgentOS gives each agent full control of the machine while maintaining safety, memory, and coordination.

---

## 🧩 What Can It Do?

- Run teams of intelligent agents
- Launch apps, browse websites, type, click, and interact with your OS
- Reflect on past errors and patch themselves
- Build and evolve new agents using Gemini CLI
- Collaborate via shared memory and structured task plans
- Simulate human-like behaviors (typing, misclicks, delays)

---

## 🧱 Core Architecture

- **AgentShell**: Base class with `think()`, `act()`, logging, memory, and supervisor checks
- **DirectorAgent**: Like a CEO — receives user goals and plans missions
- **DevAgent**: Builds new agents by prompting Gemini CLI using full project context
- **SupervisorAgent**: Monitors all actions and approves risky operations
- **SystemBrainAgent**: Reflects on agent logs and proposes improvements
- **SelfPatcherAgent**: Automatically patches code if failures are detected
- **AgentOSCore**: The runtime layer that connects actions to real-world execution (e.g. open apps, move mouse)

---

## 🔐 Local-First and Autonomous

- All agents run locally on your machine
- Agents use shared memory to coordinate
- Can operate without internet or cloud once initialized
- CLI-powered AI evolution via [Gemini CLI](https://github.com/google-gemini/gemini-cli)

---

## 📂 Project Structure

AgentOS/

├── agentos.py # Main bootloader


├── agents/ # All agents (DevAgent, WriterAgent, etc.)


│ ├── agent_shell.py


│ ├── director_agent.py


│ ├── writer_agent.py


│ ├── agent_launcher.py


│ └── ...


├── system/ # Runtime & safety layer


│ ├── agentos_core.py # Core interface to control OS (mouse, keyboard)


│ ├── supervisor.py # Monitors risky actions


│ ├── self_patcher.py # Attempts auto-fixes on agent failure


│ └── system_brain.py # Logs + reasoning on previous failures


├── memory/ # Long-term memory (JSON key-value)


│ └── memory.py


├── missions/ # Saved missions in JSON


│ └── mission_001.json


├── agents_map.json # Maps agent names to their Python modules


├── .env # API keys & CLI path (ignored by Git)


├── requirements.txt # Python dependencies


└── README.md # You're here!


---

## 🚀 Getting Started

```bash
git clone https://github.com/Harshaldorlikar/AgentOS.git
cd agentos
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python agentos.py


## 🧠 Example Goal

🧠 What do you want the agents to do?
> Create a WriterAgent that writes a motivational tweet using today’s trending topics.


AgentOS will:

1) Plan the mission

2) Build WriterAgent using Gemini CLI

3) Launch the agent and let it act autonomously

4) Monitor, reflect, and patch as needed





