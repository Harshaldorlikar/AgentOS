# agents/poster_agent.py

from tools.runtime_controller import RuntimeController
from tools.perception_controller import PerceptionController
from tools.gemini_ui_vision import analyze_ui_elements_from_pixels
from tools.display_context import DisplayContext
from system.agentos_core import AgentOSCore
import json
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

        # ✅ STEP 0: Refresh Display Context based on active window
        display_info = DisplayContext.describe()
        self.memory.save("display_context", display_info)
        print(f"[{self.name}] 🖥️ Refreshed Display Info:")
        print(f"   ↳ Resolution     : {display_info['resolution']}")
        print(f"   ↳ DPI Scaling    : {display_info['scaling_factor'] * 100:.0f}%")
        print(f"   ↳ Screen BBox    : {display_info['bbox']}")

        # STEP 1: Load tweet content
        content = self.memory.load("post_content")
        if not content:
            print(f"[{self.name}] ❌ No tweet content found.")
            return
        print(f"[{self.name}] Loaded post: {content}")

        # STEP 2: Open browser to X
        self.core.request_action(
            agent=self.name,
            action_type="open_browser",
            target="https://x.com/compose/post",
            reason="Open composer to post tweet"
        )
        time.sleep(3)

        # STEP 3: Perceive screen before typing
        pixel_array, screen_bbox = PerceptionController.capture_screen_array()
        perception = {"pixel_array": pixel_array}
        self.supervisor.update_perception(perception)

        # STEP 4: Get approval to type tweet
        approved = self.supervisor.approve_action(
            agent_name=self.name,
            action="type_text",
            value=content,
            task_context=self.task_context
        )
        if not approved:
            print(f"[{self.name}] ❌ Supervisor blocked typing.")
            return

        RuntimeController.type_text(
            text=content + " ",
            reason="Composing tweet on X"
        )

        print(f"[{self.name}] ⏳ Waiting for Post button to become active...")
        time.sleep(1.5)

        # STEP 5: Updated perception after typing
        pixel_array, screen_bbox = PerceptionController.capture_screen_array()
        perception = {"pixel_array": pixel_array}
        self.supervisor.update_perception(perception)
        print(f"[{self.name}] 👁️ Updated perception received after typing.")

        # STEP 6: Use PerceptionController to find Post buttons via smart Gemini
        task_prompt = (
            "Find all buttons labeled 'Post' in the tweet composer popup — "
            "ignore sidebar or nav or footer."
        )
        elements = PerceptionController.analyze_ui_elements(task_prompt)
        print(f"[{self.name}] 🧠 Gemini returned UI elements:\n{json.dumps(elements, indent=2)}")

        if not elements:
            print(f"[{self.name}] ❌ No UI elements found.")
            return

        # STEP 7: Filter valid Post buttons
        candidates = [
            e for e in elements
            if e.get("label", "").lower() == "post"
            and e.get("confidence", 0.0) > 0.6
            and "popup" in e.get("context", "").lower()
        ]

        if not candidates:
            print(f"[{self.name}] ❌ No valid Post button in composer popup.")
            return

        # STEP 8: Choose the most likely one
        selected = min(candidates, key=lambda b: (b["y_min"], -b["x_max"]))
        print(f"[{self.name}] ✅ Selected UI element:\n{json.dumps(selected, indent=2)}")

        # ✅ STEP 9: Calculate raw & DPI-scaled absolute click coordinates
        midpoint_x = (selected["x_min"] + selected["x_max"]) / 2
        midpoint_y = (selected["y_min"] + selected["y_max"]) / 2

        display_info = self.memory.load("display_context") or {}
        scaling_factor = display_info.get("scaling_factor", 1.0)

        abs_x = int(midpoint_x)
        abs_y = int(midpoint_y)
        label = selected.get("label", "Post")

        print(f"[{self.name}] 🧮 Raw midpoint: ({midpoint_x}, {midpoint_y})")
        print(f"[{self.name}] 🖱️ DPI-scaled click coords: ({abs_x}, {abs_y}) using scale {scaling_factor:.2f}")

        bounding_box = {
            "x_min": selected["x_min"],
            "y_min": selected["y_min"],
            "x_max": selected["x_max"],
            "y_max": selected["y_max"],
            "text": label
        }

        # STEP 10: Ask supervisor to approve click
        approved = self.supervisor.approve_action(
            agent_name=self.name,
            action="click",
            value=f"{abs_x},{abs_y}",
            task_context="Click Post button to publish tweet",
            perception=perception,
            bounding_box=bounding_box
        )
        if not approved:
            print(f"[{self.name}] ❌ Supervisor blocked the click.")
            return

        # STEP 11: Perform the click
        RuntimeController.click(abs_x, abs_y, reason="Click Post button with absolute screen coordinates")
        print(f"[{self.name}] ✅ Tweet posted successfully.")
