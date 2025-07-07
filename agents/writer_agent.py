from agents.agent_shell import AgentShell
from system.agentos_core import AgentOSCore
from memory.memory import Memory
from tools.runtime_controller import RuntimeController  # ✅ Centralized runtime intelligence

class WriterAgent(AgentShell):
    def __init__(self, name="WriterAgent"):
        super().__init__(name=name)
        self.memory = Memory()
        self.core = AgentOSCore()

    def get_trending_topics(self):
        prompt = """
Give me 5 trending Twitter hashtags for India today.
Only return a clean list like (Just Example):
- #AI
- #TechNews
- #StartupIndia
"""
        output = RuntimeController.ask_gemini(prompt)
        topics = [line.strip("- ").strip() for line in output.splitlines() if line.startswith("-")]
        return topics if topics else ["#AI", "#Motivation"]

    def think(self):
        topics = self.get_trending_topics()
        joined = " ".join(topics[:3])  # Use only top 3 for clarity
        self.content = f"Let's rise and lead the change. {joined}\n#BuildWithAI"
        self.memory.save("post_content", self.content)
        self.log(f"🧠 Generated tweet content: {self.content}")

    def act(self):
        self.core.request_action(
            agent=self.name,
            action_type="open_browser",
            target="https://x.com/compose/post",
            reason="Preparing to post the tweet"
        )

        tweet = self.memory.load("post_content")
        if tweet:
            self.core.request_action(
                agent=self.name,
                action_type="type_text",
                target=tweet,
                reason="Typing the tweet into the post box"
            )
            self.log("✅ Tweet typing requested.")
        else:
            self.log("⚠️ No tweet content available.")
