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
├── tools/
│   └── runtime_controller.py  # Gemini-powered execution of system actions (mouse, keyboard, browser)
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

---

## 📎 AgentShell Runtime API Reference

This section describes the available methods provided by the `AgentShell` class. All agents must inherit from this class to gain access to core system-level controls (apps, typing, mouse, logging, memory, etc).

### 🧠 Constructor

```python
def __init__(self, name="AgentName"):
    super().__init__(name=name)

🔧 Runtime Methods

| Method                   | Description                                |
| ------------------------ | ------------------------------------------ |
| `self.log(msg)`          | Log a message (to file + console)          |
| `self.memory.save()`     | Save internal key/value memory             |
| `self.memory.load()`     | Load memory saved earlier                  |
| `self.open_app(path)`    | Open a desktop app (e.g., Chrome, Notepad) |
| `self.type_text(txt)`    | Type out text (like a human would)         |
| `self.press_key(k)`      | Press a key (`enter`, `tab`, etc.)         |
| `self.move_mouse(x,y)`   | Move mouse to coordinates                  |
| `self.click_mouse()`     | Simulate a left-click                      |
| `self.take_screenshot()` | Capture screen and save it to logs         |

⚠️ Notes for Gemini
Use these methods instead of raw pyautogui or subprocess calls.

Never access OS directly. Use .open_app() to launch apps.

Typing must go through .type_text(), not print().

Always use .log(...) for visibility and debugging.

The Supervisor approves or blocks risky actions.

These functions are how agents physically control the machine.

🧠 Runtime Controller (Execution Layer)
This module is located in tools/runtime_controller.py and acts as the execution layer of AgentOS — controlling the actual keyboard, mouse, apps, browser, and screen like a human would.

It works under the hood of AgentOSCore, and agents never call it directly. Instead, it is triggered after Supervisor approval via:

AgentOSCore.request_action(...)

🔧 Features and Responsibilities
The RuntimeController provides intelligent control over the system, such as:

| Action            | Method                       | Description                        |
| ----------------- | ---------------------------- | ---------------------------------- |
| Open App          | `open_app(app_name, reason)` | Launches a local application       |
| Browse            | `browse(url, reason)`        | Opens a browser with the given URL |
| Type Text         | `type_text(text, reason)`    | Types text like a human            |
| Click Coordinates | `click(x, y, reason)`        | Moves and clicks the mouse         |
| Take Screenshot   | `screenshot(path, reason)`   | Captures the current screen        |

🧠 Gemini CLI Integration
Each action can be accompanied by a reason. The reason is passed to Gemini CLI, which gives intelligent feedback or suggestions before execution: RuntimeController.type_text("Hello world", reason="Filling out the login form")

Example Gemini prompt during typing:

You are typing the following content: "Hello world" for reason: "Filling out the login form". Where should you type it?

This adds situational awareness and reflection before acting.

✅ Usage Rules
❌ Never call RuntimeController methods directly from an agent.

✅ Agents must use AgentOSCore.request_action(...)

✅ AgentOSCore will call RuntimeController only if approved by the SupervisorAgent

🧩 Architecture Role
Agent → AgentShell → AgentOSCore → Supervisor → RuntimeController

This structure ensures every action is:

Requested by an agent

Evaluated for safety

Executed intelligently

Logged for review or patching

🛠️ Runtime Layer: AgentOSCore + RuntimeController

All actions from agents (typing, clicking, opening apps) must go through AgentOSCore.request_action(...)

AgentOSCore then dispatches to RuntimeController which executes the real OS-level actions via pyautogui, subprocess, browser, etc.

❌ No agent should call those libraries directly.


🧠 Runtime Layer — Real-Time Info Gathering Guidelines
If the agent’s goal includes fetching dynamic content (e.g., trending topics, news, weather, etc.):

✅ Use RuntimeController to simulate human interaction, such as:

RuntimeController.open_app("chrome") → open browser

RuntimeController.type_text("trending Twitter topics site:x.com") → simulate search

RuntimeController.click(x, y) → interact if needed

RuntimeController.screenshot(...) → capture info

RuntimeController.ask_gemini(...) → interpret screen content (if needed)

🚫 Never use:

requests, http, openai, google_web_search, or any API

Direct string scraping or parsing

✅ Use reasoning to determine:

What to type into Chrome

When to stop

What to summarize and type as output (e.g., tweet, message, note)

🧠 Example logic:

Open Chrome → search for "Trending topics Twitter India" → screenshot → ask Gemini: “What’s trending?” → create tweet → type.
