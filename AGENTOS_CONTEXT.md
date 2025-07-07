# 🧠 AgentOS — System Context Blueprint

AgentOS is an operating system for intelligent AI agents. It allows them to operate a computer like a human — through keyboard, mouse, screen, apps, files, and browser — with supervision, memory, and runtime control.

---

## 🧩 Architecture Overview

- All agents must inherit from `AgentShell`
- Each agent must define two methods:
  - `def think(self):` → for planning and internal reasoning
  - `def act(self):` → for executing tasks through the runtime
- All agent actions must be routed through:
  ```python
  AgentOSCore.request_action(agent=..., action_type=..., target=..., reason=...)

- All logs must use: self.log(...)

- Memory is accessed via: self.memory.save("key", value) and .load("key")

Project Structure :


AgentOS/
├── agentos.py                  # Bootloader for the OS and agents
├── AGENTOS_CONTEXT.md          # This file (system blueprint)
├── agents/
│   ├── agent_shell.py         # All agents inherit from this
│   ├── director_agent.py      # The CEO of the agent team
│   ├── dev_agent.py           # Builds new agents from user goals using Gemini CLI
│   ├── poster_agent.py        # Posts output (like tweets)
│   └── writeragent.py         # [Example] Generates written content
├── system/
│   ├── agentos_core.py        # Runtime layer (type, open app, browser, etc.)
│   ├── supervisor.py          # Blocks dangerous or unnecessary actions
│   └── self_patcher.py        # Detects and patches broken agents
├── memory/
│   └── memory.py              # JSON-based local memory per agent
├── missions/
│   └── mission_001.json       # A step-by-step plan for agents to execute
├── agents_map.json            # Maps agent names to Python module paths



✅ Coding Guidelines (Required):

- Class must inherit from AgentShell
  Use: 
   
   def __init__(self, name="AgentName"):
    super().__init__(name=name)

- Use self.memory.save(...) and self.memory.load(...) to store context between agents

- Do not call print() — use self.log(...)

- Do not execute anything directly — all system interaction must go through AgentOSCore


🚫 Forbidden (must not be used):

❌ Do not use requests, openai, urllib, google_web_search

❌ Do not use subprocess, os.system, or direct API/web calls

❌ Do not hardcode external links, API calls, or screen scraping

❌ Do not define a class named Agent

✅ Example Agent (fully valid):

from agents.agent_shell import AgentShell
from system.agentos_core import AgentOSCore
from memory.memory import Memory

class WriterAgent(AgentShell):
    def __init__(self, name="WriterAgent"):
        super().__init__(name=name)
        self.memory = Memory()
        self.core = AgentOSCore()

    def think(self):
        # Prepare the content
        self.content = "Stay focused and keep building! #Motivation"
        self.memory.save("post_content", self.content)
        self.log(f"Saved tweet to memory: {self.content}")

    def act(self):
        self.core.request_action(
            agent=self.name,
            action_type="post_tweet",
            target="X",
            reason="Posting motivational tweet",
            data=self.content
        )
        self.log("Tweet post requested via AgentOSCore.")

🎯 Mission Plan Format:

- Each mission is saved in missions/mission_001.json like this:

{
  "goal": "Create a motivational tweet and post it",
  "steps": [
    { "agent": "WriterAgent", "task": "Write a motivational tweet", "status": "pending" },
    { "agent": "PosterAgent", "task": "Post the tweet", "status": "pending" }
  ]
}

🧠 Supervisor Agent (at runtime):

All actions are reviewed by a SupervisorAgent. It approves actions like:

"open_app" or "open_browser"

"type_text" or "post_tweet"

"click_element" or "screenshot"

Rejection messages should be logged, but agents must not crash or re-attempt.


🤖 How to Add New Agents:

The DevAgent uses Gemini CLI to generate new agents.

Agents are stored in agents/ as agentname.py

The module path is updated in agents_map.json:

{
  "WriterAgent": "agents.writeragent",
  "PosterAgent": "agents.poster_agent"
}

💡 System Brain & Self-Patcher:

- The SystemBrain reviews logs for patterns, failures, or inefficiencies

- The SelfPatcher can attempt fixes or raise repair tasks

- These enable AgentOS to self-correct and evolve over time.

These enable AgentOS to self-correct and evolve over time.

🗂️ File Access Guidelines for Gemini CLI:

If needed to complete the task:

You may inspect or reference any files in the project directory, including:

agents/: contains all AI agents.

system/: runtime tools like AgentOSCore, supervisor, patcher.

memory/: logging, memory storage, system reflection.

missions/: JSON files that define goals, steps, and status.

agentos.py: main boot file.

Use file structure to understand dependencies, base classes, or tools.

Never import third-party APIs like requests, openai, or http.

Always integrate with the AgentOS Runtime Layer by calling AgentOSCore.request_action(...).

Only write valid agent code. No explanations or markdown.