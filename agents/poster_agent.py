from tools.runtime_controller import RuntimeController
from tools.perception_controller import PerceptionController
from tools.gemini_ui_vision import analyze_ui_elements_from_pixels
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

        # Load tweet content
        content = self.memory.load("post_content")
        if not content:
            print(f"[{self.name}] ❌ No tweet content found.")
            return
        print(f"[{self.name}] Loaded post: {content}")

        # Open Twitter composer
        self.core.request_action(
            agent=self.name,
            action_type="open_browser",
            target="https://x.com/compose/post",
            reason="Open composer to post tweet"
        )
        time.sleep(3)

        # STEP 1: Initial screen perception
        pixel_array = PerceptionController.capture_screen_array()
        perception = {"pixel_array": pixel_array}
        self.supervisor.update_perception(perception)

        # STEP 2: Supervisor approval to type
        approved = self.supervisor.approve_action(
            agent_name=self.name,
            action="type_text",
            value=content,
            task_context=self.task_context
        )
        if not approved:
            print(f"[{self.name}] ❌ Supervisor blocked typing.")
            return

        # Type tweet content
        RuntimeController.type_text(
            text=content + " ",
            reason="Composing tweet on X"
        )

        print(f"[{self.name}] ⏳ Waiting for Post button to become active...")
        time.sleep(1.5)

        # STEP 3: Capture updated perception after typing
        pixel_array = PerceptionController.capture_screen_array()
        perception = {"pixel_array": pixel_array}
        self.supervisor.update_perception(perception)
        print(f"[{self.name}] 👁️ Updated perception received after typing.")

        # STEP 4: Analyze UI for "Post" buttons
        task_prompt = "Find all buttons labeled 'Post' in the tweet composer popup — ignore sidebar or nav."
        elements = analyze_ui_elements_from_pixels(pixel_array, task_prompt)

        if not elements:
            print(f"[{self.name}] ❌ No UI elements found.")
            return

        # Filter candidates by label, confidence, and popup region
        candidates = [
            e for e in elements
            if e.get("label", "").lower() == "post"
            and e.get("confidence", 0.0) > 0.6
            and "popup" in e.get("context", "").lower()
        ]

        if not candidates:
            print(f"[{self.name}] ❌ No valid Post button in composer popup.")
            return

        # Prioritize topmost, right-aligned buttons
        selected = min(candidates, key=lambda b: (b["y_min"], -b["x_max"]))

        # Derive center click position
        x = (selected["x_min"] + selected["x_max"]) // 2
        y = (selected["y_min"] + selected["y_max"]) // 2
        label = selected.get("label", "Post")

        bounding_box = {
            "x_min": selected["x_min"],
            "y_min": selected["y_min"],
            "x_max": selected["x_max"],
            "y_max": selected["y_max"],
            "text": label
        }

        # STEP 5: Supervisor approval to click
        approved = self.supervisor.approve_action(
            agent_name=self.name,
            action="click",
            value=f"{x},{y}",
            task_context="Click Post button to publish tweet",
            perception=perception,
            bounding_box=bounding_box
        )
        if not approved:
            print(f"[{self.name}] ❌ Supervisor blocked the click.")
            return

        # STEP 6: Perform the click
        RuntimeController.click(x, y, reason="Click Post button to submit tweet")
        print(f"[{self.name}] ✅ Tweet posted successfully.")
