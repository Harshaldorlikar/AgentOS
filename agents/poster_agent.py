from agents.agent_shell import AgentShell
from memory.memory import Memory
from system.agentos_core import AgentOSCore
from tools.runtime_controller import RuntimeController

class PosterAgent(AgentShell):
    def __init__(self, name="PosterAgent"):
        super().__init__(name=name)
        self.memory = Memory()
        self.core = AgentOSCore()

    def think(self):
        self.post = self.memory.load("post_content")
        if not self.post:
            self.log("❌ No post content found in memory.")
        else:
            self.log(f"Loaded post: {self.post}")

    def act(self):
        if not self.post:
            self.log("❌ Aborting: No content to post.")
            return

        # Step 1: Open Twitter Compose
        self.core.request_action(
            agent=self.name,
            action_type="open_browser",
            target="https://x.com/compose/post",
            reason="Prepare to post the tweet"
        )

        # Step 2: Type the tweet
        self.core.request_action(
            agent=self.name,
            action_type="type_text",
            target=self.post,
            reason="Typing tweet into compose box"
        )

        # Step 3: Wait briefly for Post button to activate
        self.log("⏳ Waiting for UI to reflect typed content...")
        self.sleep(2)

        # Step 4: Take screenshot and perceive UI
        perception = self.core.request_action(
            agent=self.name,
            action_type="perceive",
            target="X",
            reason="Locate the Post button"
        )

        if not perception or not isinstance(perception, dict):
            self.log("❌ No perception data received. Cannot proceed.")
            return

        # Step 5: Search for "Post" button
        ui_elements = perception.get("ui_elements", [])
        post_button = None
        for el in ui_elements:
            if el["text"].strip().lower() == "post":
                post_button = el
                break

        if not post_button:
            self.log("❌ 'Post' button not found. UI might still be loading.")
            return

        x = post_button["left"] + post_button["width"] // 2
        y = post_button["top"] + post_button["height"] // 2

        # Step 6: Click the "Post" button
        self.core.request_action(
            agent=self.name,
            action_type="click",
            target=f"{x},{y}",
            reason="Clicking Post button to submit tweet"
        )
        self.log("✅ Post submitted.")
