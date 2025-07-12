# agents/writer_agent.py

from agents.agent_shell import AgentShell
from system.agentos_core import AgentOSCore
from memory.memory import Memory
from tools.gemini_interface import ask_gemini

class WriterAgent(AgentShell):
	def __init__(self, name="WriterAgent"):
		super().__init__(name=name)
		self.memory = Memory()
		self.core = AgentOSCore()
		self.task_context = "Write a motivational tweet using trending topics"

	def think(self):
		trending_prompt = "Give me 2 trending Twitter hashtags in India today. Respond with only the hashtags separated by spaces."
		trending = ask_gemini(trending_prompt)

		self.tweet = f"Let’s rise and lead the change.\n{trending}\n#Motivation #BuildWithAI"
		self.memory.save("post_content", self.tweet)
		self.log(f"🧠 Trending topics: {trending}")
		self.log("✅ Composed tweet and saved to memory.")

	def act(self):
		self.log("✅ Nothing to do. Tweet saved for PosterAgent.")