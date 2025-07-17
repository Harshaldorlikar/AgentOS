# agents/poster_agent.py

import json
import time
import logging
import os
# ❌ The PosterAgent no longer needs to import RuntimeController directly.
from tools.perception_controller import PerceptionController
from tools.gemini_ui_vision import analyze_ui_elements_from_pixels
from tools.display_context import DisplayContext
from system.agentos_core import AgentOSCore # ✅ Import the core

# Configure logging for this agent
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DEBUG_VISION_ENABLED = os.getenv('AGENTOS_DEBUG_VISION', 'false').lower() == 'true'

class PosterAgent:
    """
    An autonomous agent that posts content by requesting actions through the AgentOSCore.
    """
    # ✅ __init__ now accepts the core object
    def __init__(self, memory, supervisor, core: AgentOSCore):
        self.memory = memory
        self.supervisor = supervisor
        self.core = core # ✅ Store the core instance
        self.name = "PosterAgent"
        self.task_context = "Post content to X (Twitter)"

    def _calculate_logical_coords(self, selected_button: dict, scaling_factor: float) -> tuple[int, int] | None:
        """
        Converts physical pixel coordinates to logical coordinates by dividing by the scale factor.
        """
        if "bounding_box" not in selected_button:
            logger.error("Selected element is missing the 'bounding_box' key.")
            return None

        bbox = selected_button["bounding_box"]
        midpoint_x_physical = (bbox["x_min"] + bbox["x_max"]) / 2
        midpoint_y_physical = (bbox["y_min"] + bbox["y_max"]) / 2
        x_logical = int(midpoint_x_physical / scaling_factor)
        y_logical = int(midpoint_y_physical / scaling_factor)
        return x_logical, y_logical

    def run(self):
        """Executes the full workflow for the PosterAgent."""
        logger.info(f"Agent '{self.name}' started running.")

        display_info = DisplayContext.describe()
        logger.info(f"Using Display Info: {display_info['resolution']} @ {display_info['scaling_factor']*100:.0f}% scaling.")

        content_to_post = self.memory.load("post_content")
        if not content_to_post:
            logger.error("No post content found in memory. Aborting.")
            return
        
        # --- FIX: All actions are now requested through the core ---
        self.core.request_action(self.name, "browse", "https://x.com/compose/post", "Open composer to post tweet")
        time.sleep(4)
        self.core.request_action(self.name, "type_text", content_to_post + " ", "Composing the tweet content")
        time.sleep(3)

        for attempt in range(2):
            logger.info(f"Perception Attempt #{attempt + 1}")

            pixel_array, _ = PerceptionController.capture_primary_monitor()
            if pixel_array is None:
                logger.error("Failed to capture screen.")
                time.sleep(1)
                continue
            
            if DEBUG_VISION_ENABLED:
                debug_image_path = os.path.join(os.getenv('TEMP', '/tmp'), f"agent_view_attempt_{attempt + 1}.png")
                PerceptionController.save_screen_snapshot(pixel_array, debug_image_path)
                logger.info(f"Saved debug screenshot to: {debug_image_path}")

            self.supervisor.update_perception(pixel_array)

            task_prompt = "Locate the clickable 'Post' button inside the tweet composer popup."
            elements = analyze_ui_elements_from_pixels(pixel_array, task_prompt)
            if not elements:
                logger.warning("Vision model returned no elements.")
                time.sleep(1)
                continue

            logger.info(f"Raw elements from Gemini:\n{json.dumps(elements, indent=2)}")

            valid_buttons = [
                e for e in elements
                if isinstance(e, dict) and "post" in e.get("label", "").lower()
            ]

            if not valid_buttons:
                logger.warning("No valid 'Post' button found after filtering.")
                time.sleep(1)
                continue

            selected_button = min(valid_buttons, key=lambda b: b.get("bounding_box", {}).get("y_min", float('inf')))
            logger.info(f"Selected button for action:\n{json.dumps(selected_button, indent=2)}")

            coords = self._calculate_logical_coords(selected_button, display_info['scaling_factor'])
            if coords is None:
                continue
            
            logical_x, logical_y = coords
            logger.info(f"Calculated LOGICAL click coords: ({logical_x}, {logical_y})")

            # --- FIX: The final click is also requested through the core ---
            click_successful = self.core.request_action(
                agent_name=self.name,
                action_type="click",
                value=f"{logical_x},{logical_y}",
                task_context="Clicking the final Post button"
            )

            if click_successful:
                logger.info("Click successful. Task complete.")
                return

        logger.error("All attempts failed to post the tweet.")
