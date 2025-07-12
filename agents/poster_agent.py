# agents/poster_agent.py

from tools.runtime_controller import RuntimeController
from tools.perception_controller import PerceptionController
from tools.gemini_interface import find_button_from_pixels
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

		content = self.memory.load("post_content")
		if not content:
			print(f"[{self.name}] ❌ No tweet content found.")
			return
		print(f"[{self.name}] Loaded post: {content}")

		self.core.request_action(
			agent=self.name,
			action_type="open_browser",
			target="https://x.com/compose/post",
			reason="Open composer to post tweet"
		)

		time.sleep(3)

		pixel_array = PerceptionController.capture_screen_array()
		perception = {"pixel_array": pixel_array}
		self.supervisor.update_perception(perception)

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

		pixel_array = PerceptionController.capture_screen_array()
		perception = {"pixel_array": pixel_array}
		self.supervisor.update_perception(perception)

		print(f"[{self.name}] 👁️ Updated perception received after typing.")

		button = find_button_from_pixels(pixel_array, target_label="Post")
		if not button or "x" not in button or "y" not in button:
			print(f"[{self.name}] ❌ Could not find the Post button.")
			return

		x, y, text = button["x"], button["y"], button.get("label", "Post")

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

		RuntimeController.click(x, y, reason="Click Post button to submit tweet")
		print(f"[{self.name}] ✅ Tweet posted successfully.")