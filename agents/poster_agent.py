# agents/poster_agent.py

from agents.agent_shell import AgentShell
from memory import memory
from system.agentos_core import AgentOSCore

class PosterAgent(AgentShell):
    def __init__(self, name="PosterAgent"):
        super().__init__(name=name)
        self.memory = memory.Memory()
        self.core = AgentOSCore()

    def think(self):
        self.task_context = "Post content to X (Twitter) using Chrome browser use the Harshal Main Profile."
        self.log("Thinking... preparing to post something.")
        self.post = self.memory.load("draft_posts")
        if self.post:
            self.log(f"Loaded post: {self.post[0]}")
        else:
            self.log("No draft posts found.")

    def act(self):
        self.log("Requesting browser open via AgentOSCore...")
        self.core.request_action(
            agent=self.name,
            action_type="open_browser",
            target="https://x.com",
            reason=self.task_context
        )

        # Optionally add mouse typing behavior here later
        # self.core.request_action(self.name, "type_text", self.post[0], self.task_context)
