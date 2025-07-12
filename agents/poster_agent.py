# agents/poster_agent.py

from tools.runtime_controller import RuntimeController
from tools.perception_controller import PerceptionController
from system.agentos_core import AgentOSCore
import time

class PosterAgent:
    def __init__(self, memory, supervisor):
        self.memory = memory
        self.supervisor = supervisor
        self.core = AgentOSCore()
        self.name = "PosterAgent"
        self.task_context = "Post content to X (Twitter)"

    def run(self):
        print(f"[{self.name}] Agent started running.")

        # Step 1: Load tweet content from memory
        content = self.memory.load("post_content")
        if not content:
            print(f"[{self.name}] ❌ No tweet content found.")
            return
        print(f"[{self.name}] Loaded post: {content}")

        # Step 2: Open X.com compose page
        self.core.request_action(
            agent=self.name,
            action_type="open_browser",
            target="https://x.com/compose/post",
            reason="Open composer to post tweet"
        )

        # Step 3: Let browser stabilize and get perception
        time.sleep(3)
        perception = PerceptionController.get_perception_snapshot()
        self.supervisor.update_perception(perception)

        # Step 4: Ask Supervisor for typing approval
        approved = self.supervisor.approve_action(
            agent_name=self.name,
            action="type_text",
            value=content,
            task_context=self.task_context
        )
        if not approved:
            print(f"[{self.name}] ❌ Supervisor blocked typing.")
            return

        # Step 5: Type the content with trailing space to collapse hashtag suggestion
        RuntimeController.type_text(
            text=content + " ",
            reason="Composing tweet on X"
        )

        # Step 6: Wait a bit for UI to update the button state
        print(f"[{self.name}] ⏳ Waiting for Post button to become active...")
        time.sleep(1.5)

        # Step 7: Refresh perception after typing
        perception = PerceptionController.get_perception_snapshot()
        self.supervisor.update_perception(perception)
        print(f"[{self.name}] 👁️ Updated perception received after typing.")

        # Step 8: Use Gemini to find Post button via image + OCR
        x, y, text = RuntimeController.find_button_gemini("Post", perception_data=perception)
        if not x or not y:
            print(f"[{self.name}] ❌ Could not find the Post button.")
            return

        # Step 9: Ask Supervisor to approve click
        approved = self.supervisor.approve_action(
            agent_name=self.name,
            action="click",
            value=f"{x},{y}",
            task_context="Click Post button to publish tweet",
            perception=perception,
            bounding_box={"x": x, "y": y, "text": text}
        )
        if not approved:
            print(f"[{self.name}] ❌ Supervisor blocked the click.")
            return

        # Step 10: Click the button
        RuntimeController.click(x, y, reason="Click Post button to submit tweet")
        print(f"[{self.name}] ✅ Tweet posted successfully.")