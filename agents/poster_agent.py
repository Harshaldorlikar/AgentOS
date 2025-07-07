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
        self.post_content = self.memory.load("post_content")

        if not self.post_content:
            self.log("⚠️ No post content found in memory.")
        else:
            self.log(f"Loaded post: {self.post_content}")

    def act(self):
        if not self.post_content:
            self.log("⚠️ Skipping action — no post content to share.")
            return

        # Step 1: Open the X composer
        self.core.request_action(
            agent=self.name,
            action_type="open_browser",
            target="https://x.com/compose/post",
            reason="Open Twitter to post content"
        )

        # Step 2: Type the post
        self.core.request_action(
            agent=self.name,
            action_type="type_text",
            target=self.post_content,
            reason="Typing post into Twitter"
        )

        # Step 3: Optionally simulate Enter to post
        approved = self.supervisor.approve_action(
            agent_name=self.name,
            action="press_key",
            value="enter",
            task_context="Post the tweet"
        )

        if approved:
            self.press_key("enter")
            self.log("✅ Simulated Enter key to post the tweet.")
        else:
            self.log("⏸️ Posting not completed. Supervisor blocked Enter key.")
