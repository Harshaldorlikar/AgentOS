# agents/writeragent.py

from agents.agent_shell import AgentShell
from system.agentos_core import AgentOSCore
from memory.memory import Memory
from tools.runtime_controller import RuntimeController

class WriterAgent(AgentShell):
    def __init__(self, name="WriterAgent"):
        super().__init__(name=name)
        self.memory = Memory()
        self.core = AgentOSCore()

    def think(self):
        # Get trending hashtags
        trending_prompt = "Give me 2 trending Twitter hashtags in India today, just the hashtags, no numbers or commentary."
        trending = RuntimeController.ask_gemini(trending_prompt)

        # Compose tweet
        self.tweet = f"Let’s rise and lead the change. {trending}\n#Motivation #BuildWithAI"
        self.memory.save("post_content", self.tweet)
        self.log(f"🧠 Trending topics: {trending}")
        self.log("✅ Composed tweet and saved to memory.")

    def act(self):
        self.log("✅ Nothing to do. Tweet saved for PosterAgent.")
