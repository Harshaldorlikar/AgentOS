# agents/poster_agent.py

from agents.agent_shell import AgentShell
from system.agentos_core import AgentOSCore
from memory.memory import Memory

class PosterAgent(AgentShell):
    def __init__(self, name="PosterAgent"):
        super().__init__(name=name)
        self.memory = Memory()
        self.core = AgentOSCore()

    def think(self):
        self.log("Thinking... preparing to post something.")
        self.tweet = self.memory.load("post_content")

        if not self.tweet:
            self.tweet = "Stay positive and take action. #Motivation"
            self.log("⚠️ No tweet in memory. Using fallback tweet.")
        else:
            self.log(f"Loaded post: {self.tweet}")

    def act(self):
        # Open tweet composer on X
        self.core.request_action(
            agent=self.name,
            action_type="open_browser",
            target="https://x.com/compose/post",
            reason="Open composer to post the tweet"
        )

        # Type tweet
        self.core.request_action(
            agent=self.name,
            action_type="type_text",
            target=self.tweet,
            reason="Type the tweet"
        )

        # ⏱️ Wait a little before clicking (ensure page loads)
        import time
        time.sleep(3)  # Adjust if needed

        # 👇 Hardcoded coordinates — replace with your actual position
        self.core.request_action(
            agent=self.name,
            action_type="click",
            target="950,294",  # << Replace with your actual Post button coords
            reason="Click Post button to submit tweet"
        )

        self.log("✅ Post button click requested.")
