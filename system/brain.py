# system/brain.py

import logging
import asyncio
import json
import re
import numpy as np
from tools.web_controller import WebController
from tools.perception_controller import PerceptionController
from tools.gemini_ui_vision import smart_vision_query
from system.agentos_core import AgentOSCore
from agents.supervisor import SupervisorAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Brain:
    """
    The central cognitive system for AgentOS. It orchestrates the entire
    perceive-think-act loop to achieve high-level goals using a stateful,
    reasoning-driven approach with Gemini 1.5 Pro.
    """
    def __init__(self, core: AgentOSCore, supervisor: SupervisorAgent):
        """
        Initializes the Brain with the shared AgentOSCore and supervisor.
        """
        self.core = core
        self.supervisor = supervisor
        self.web_controller: WebController = self.core.web_controller
        self.perception_controller = PerceptionController()
        # The history stores the chain of thought for the mission
        self.history = []

    async def _initialize_connections(self) -> bool:
        """Connects to necessary external resources, like the browser."""
        logger.info("Brain initializing connections...")
        return await self.web_controller.connect()

    async def _shutdown_connections(self):
        """Gracefully disconnects from external resources."""
        logger.info("Brain shutting down connections...")
        await self.web_controller.close()

    async def perceive_environment(self) -> dict:
        """
        Gathers a multimodal understanding of the current environment.
        """
        logger.info("🧠 Perceiving environment...")
        
        full_screen_pixels, _ = self.perception_controller.capture_primary_monitor()
        if full_screen_pixels is None:
            return {"error": "Screen capture failed."}

        dom_tree = await self.web_controller.extract_full_dom_with_bounding_rects()
        
        observation = {
            "dom_tree": dom_tree,
            "full_screenshot_pixels": full_screen_pixels
        }
        
        logger.info(f"Perception complete. Found {len(dom_tree) if dom_tree else 0} visible DOM elements.")
        return observation

    async def decide_next_action(self, goal: str, observation: dict) -> dict | None:
        """
        Uses Gemini 1.5 Pro to decide the next best action by reasoning about
        the mission goal and the history of previous steps.
        """
        logger.info("🤔 Thinking... Deciding next action with Gemini 1.5 Pro.")
        
        dom_tree = observation.get("dom_tree") or []
        simplified_dom = [
            {
                "tag": el.get("tagName"),
                "label": el.get("attributes", {}).get("aria-label") or el.get("innerText", "")[:75],
                "selector": f"#{el.get('id')}" if el.get('id') else f".{el.get('className').split(' ')[0]}" if el.get('className') else el.get('tagName')
            }
            for el in dom_tree if el
        ]

        prompt = f"""
        You are the brain of an autonomous AI agent. Your high-level goal is: "{goal}"
        
        **CRITICAL INSTRUCTION:** The correct URL for the Twitter/X compose page is exactly `https://x.com/compose/post`. Do not use any other URL like 'compose/tweet'.

        History of previous actions and outcomes: {json.dumps(self.history, indent=2)}
        Current observation of the screen and DOM: {json.dumps(simplified_dom, indent=2)}

        Based on the goal and history, what is the single next logical step?
        Available Actions: BROWSE(url), TYPE(selector, text), CLICK(selector), FINISH(reason), FAIL(reason).
        Respond with a single JSON object with your "reasoning" and the "action" to take.
        Example: {{"reasoning": "I need to log in first.", "action": {{"name": "TYPE", "selector": "#username", "text": "my_user"}}}}
        """
        
        response_text = smart_vision_query(observation["full_screenshot_pixels"], prompt, models=["gemini-1.5-pro-latest"])
        if not response_text:
            return {"action": {"name": "FAIL", "reason": "Vision model failed to respond."}}
            
        try:
            match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not match: raise json.JSONDecodeError("No JSON object found", response_text, 0)
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from brain's decision response: {response_text}")
            return {"action": {"name": "FAIL", "reason": "Could not parse decision from vision model."}}

    async def execute_action(self, action: dict, goal: str, pixels: np.ndarray) -> bool:
        """
        Executes a given action by requesting it through the AgentOSCore.
        """
        if not isinstance(action, dict) or "name" not in action:
            logger.error(f"Invalid action format: {action}")
            return False

        # Update supervisor's perception BEFORE asking for approval
        self.supervisor.update_perception(pixels)

        action_name = action.get("name").lower()
        
        # The Brain now gets approval from the supervisor BEFORE executing the action.
        is_approved = self.supervisor.approve_action("Brain", action_name, action, goal)
        if not is_approved:
            return False
            
        if action_name == "browse":
            return await self.core.request_action("Brain", "browse", action.get("url"), goal)
        elif action_name == "type":
            value = {"selector": action.get("selector"), "text": action.get("text")}
            return await self.core.request_action("Brain", "type_text_web", value, goal)
        elif action_name == "click":
            return await self.core.request_action("Brain", "click_web", action.get("selector"), goal)
        
        return True # For FINISH/FAIL actions

    async def run_mission(self, goal: str):
        """
        The main control loop that runs a mission from start to finish.
        Includes a retry mechanism for failed actions.
        """
        if not await self._initialize_connections():
            logger.error("Brain could not initialize connections. Aborting mission.")
            return

        self.history = []
        
        try:
            max_steps = 10
            retry_count = 0
            max_retries = 2

            for i in range(max_steps):
                logger.info(f"\n--- Mission Step {i+1}/{max_steps} ---")
                
                observation = await self.perceive_environment()
                if "error" in observation:
                    self.history.append({"thought": "Perception failed, cannot continue."})
                    break

                decision = await self.decide_next_action(goal, observation)
                if not decision:
                    self.history.append({"thought": "Failed to make a decision."})
                    break

                action = decision.get("action")
                thought = decision.get("reasoning")
                
                self.history.append({"thought": thought, "action": action})

                if not action or action.get("name").upper() in ["FINISH", "FAIL"]:
                    logger.info(f"Mission ended with status: {action.get('name').upper() if action else 'FAIL'}. Reason: {action.get('reason', 'N/A') if action else 'No action decided.'}")
                    break
                
                success = await self.execute_action(action, goal, observation["full_screenshot_pixels"])
                self.history[-1]["outcome"] = "Success" if success else "Failure"
                
                if not success:
                    logger.error("Action execution failed.")
                    retry_count += 1
                    if retry_count > max_retries:
                        logger.error(f"Action failed more than {max_retries} times. Aborting mission.")
                        break
                    logger.warning(f"Retrying... ({retry_count}/{max_retries})")
                else:
                    retry_count = 0 

                await asyncio.sleep(2)
        finally:
            await self._shutdown_connections()
