# agentos.py

print("🚀 Booting AgentOS v0.1...")

# Step 1: Basic system boot
print("✅ System initialized.")
print("🧠 Memory system loading...")

from memory.memory import Memory
brain = Memory()

# Save boot message
brain.save("boot_message", "AgentOS has launched successfully.")
msg = brain.load("boot_message")
print(f"Memory Check: {msg}")

# Step 2: Run system intelligence agents
from system.system_brain import SystemBrainAgent
from system.self_patcher import SelfPatcherAgent

system_brain = SystemBrainAgent()
system_brain.run()

patcher = SelfPatcherAgent()
patcher.run()

# Step 3: Launch Director to get user input
from agents.director_agent import DirectorAgent
print("\n🎬 Launching DirectorAgent...\n")
director = DirectorAgent()
director.run()

# Step 4: Launch DevAgent to generate new agents if needed
from agents.dev_agent import DevAgent
print("\n🧑‍💻 Running DevAgent to build agents from goal...\n")
dev = DevAgent()
dev.run()

# Step 5: Launch generated agents
from agents.agent_launcher import AgentLauncher
print("\n🚀 Launching agents as per mission plan...\n")
launcher = AgentLauncher()
launcher.launch_agents()





