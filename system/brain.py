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

    # NOTE: The connect() and close() calls are now correctly handled by agentos.py,
    # so the _initialize_connections and _shutdown_connections methods are no longer needed here.

    async def perceive_environment(self) -> dict:
        """
        Gathers a multimodal understanding of the current environment.
        """
        logger.info("🧠 Perceiving environment...")
        
        # This function now relies solely on the WebController for web-based perception.
        dom_tree = await self.web_controller.extract_full_dom_with_bounding_rects()
        
        observation = {
            "dom_tree": dom_tree,
        }
        
        logger.info(f"Perception complete. Found {len(dom_tree) if dom_tree else 0} visible DOM elements.")
        return observation

    async def decide_next_action(self, goal: str, observation: dict) -> dict | None:
        """
        Uses Gemini 1.5 Pro to decide the next best action by reasoning about
        the mission goal and the history of previous steps.
        """
        logger.info("🤔 Thinking... Deciding next action with Gemini 1.5 Pro.")
        
        # A screenshot is still needed for the multimodal prompt to understand the visual context.
        pixels, _ = self.perception_controller.capture_primary_monitor()
        if pixels is None:
            return {"action": {"name": "FAIL", "reason": "Screen capture failed."}}

        dom_tree = observation.get("dom_tree") or []
        # Create a more compact and relevant representation of the DOM for the prompt.
        simplified_dom = [
            {
                "text": el.get("text"),
                "attributes": el.get("attributes")
            }
            for el in dom_tree if el.get("text") # Only include elements with text for brevity
        ]


        prompt = f"""
        You are the brain of an autonomous AI agent. Your high-level goal is: "{goal}"

        **CRITICAL INSTRUCTIONS FOR SELECTORS:**
        1. You MUST use standard CSS selectors. Do NOT use non-standard selectors like `:contains()`.
        2. To click a link or button with specific text, like "Click Me", use a selector that checks for that text. The best format is `a:has-text('Click Me')` or `button:has-text('Click Me')`.
        3. For elements on X.com: the tweet input area is `[data-testid='tweetTextarea_0']` and the main post button is `[data-testid='tweetButton']`.

        **CRITICAL INSTRUCTIONS FOR VERIFICATION:**
        After you perform an important action like clicking a 'Post' or 'Submit' button, your NEXT action should be to verify the result. Observe the screen. If the button you clicked is gone or the page has visibly changed, your action was likely successful, and you can `FINISH`. If the button is still there, your action failed, and you should `FAIL`.

        **History of previous actions and outcomes:**
        {json.dumps(self.history, indent=2)}

        **Current observation of visible UI elements:**
        {json.dumps(simplified_dom, indent=2)}

        Based on the goal, history, and the critical instructions above, what is the single next logical step?
        Available Actions: BROWSE(url), TYPE(selector, text), CLICK(selector), FINISH(reason), FAIL(reason).
        
        Respond with a single JSON object containing your "reasoning" and the "action" to take.
        Example: {{"reasoning": "The goal is to click the 'How to Do Great Work' essay. I will use the has-text selector.", "action": {{"name": "CLICK", "selector": "a:has-text('How to Do Great Work')"}}}}
        """
        
        response_text = smart_vision_query(pixels, prompt, models=["gemini-1.5-pro-latest"])
        
        if not response_text:
            return {"action": {"name": "FAIL", "reason": "Vision model failed to respond."}}
            
        try:
            match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not match: raise json.JSONDecodeError("No JSON object found", response_text, 0)
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from brain's decision response: {response_text}")
            return {"action": {"name": "FAIL", "reason": "Could not parse decision from vision model."}}

    async def execute_action(self, action: dict) -> bool:
        """
        Executes a given action by calling the appropriate web_controller method.
        """
        if not isinstance(action, dict) or "name" not in action:
            logger.error(f"Invalid action format: {action}")
            return False

        action_name = action.get("name").lower()
        
        try:
            if action_name == "browse":
                await self.web_controller.browse(action.get("url"))
            elif action_name == "type":
                await self.web_controller.type(action.get("selector"), action.get("text"))
            elif action_name == "click":
                # UPGRADE: For stubborn buttons like on X.com, we default to a force click.
                # This check makes the brain "smarter" about which clicks need to be forced.
                force_click = "x.com" in self.web_controller.page.url 
                await self.web_controller.click(action.get("selector"), force=force_click)
            elif action_name in ["finish", "fail"]:
                return True # These actions don't interact with the browser, so they succeed by default.
            else:
                logger.warning(f"Unknown action '{action_name}' requested by Brain.")
                return False
            return True
        except Exception as e:
            logger.error(f"Brain action '{action_name}' failed during execution: {e}")
            return False

    async def run_mission(self, goal: str) -> bool:
        """
        The main control loop that runs a mission from start to finish.
        Returns True if the mission finished successfully, False otherwise.
        """
        self.history = []
        max_steps = 15 # Increased max steps for more complex tasks
        final_status = False # Default to failure

        for i in range(max_steps):
            logger.info(f"\n--- Brain Mission Step {i+1}/{max_steps} (Goal: {goal[:60]}...) ---")
            
            try:
                observation = await self.perceive_environment()
                
                decision = await self.decide_next_action(goal, observation)
                if not decision:
                    self.history.append({"thought": "Failed to make a decision.", "outcome": "Failure"})
                    break

                action = decision.get("action")
                thought = decision.get("reasoning")
                self.history.append({"thought": thought, "action": action})

                action_name = action.get("name", "").upper()
                if not action or action_name in ["FINISH", "FAIL"]:
                    logger.info(f"Mission ended by Brain. Status: {action_name}.")
                    if action_name == "FINISH":
                        final_status = True # Mission was a success
                    break
                
                success = await self.execute_action(action)
                self.history[-1]["outcome"] = "Success" if success else "Failure"
                
                if not success:
                    logger.error("Action execution failed. Breaking mission loop.")
                    break

                await asyncio.sleep(2) # A short pause between steps to be more human-like

            except Exception as e:
                logger.error(f"A critical error occurred in the brain's mission loop: {e}", exc_info=True)
                break
        
        return final_status