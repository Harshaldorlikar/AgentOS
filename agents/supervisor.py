# agents/supervisor.py

import json
import logging
import re
from datetime import datetime
import numpy as np
from tools.gemini_ui_vision import smart_vision_query
from tools.web_controller import WebController
from tools.display_context import DisplayContext  # To convert physical to logical coordinates

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SupervisorAgent:
    """
    Acts as a selective safety and validation layer for other agents.
    It intervenes only on high-risk actions, allowing routine tasks to proceed
    without micromanagement.
    """
    def __init__(self):
        self.logs = []
        self.last_perception_pixels: np.ndarray | None = None
        self.web_controller = WebController()  # Used for resolving selectors only
        self.high_risk_keywords = [
            "post", "delete", "confirm", "purchase", "send", "submit",
            "login", "password", "credentials", "pay", "buy", "approve"
        ]

    def update_perception(self, pixels: np.ndarray):
        """
        Stores the latest visual snapshot (pixel array) from the active agent or Brain.
        This is crucial for performing visual validation on high-risk actions.
        """
        self.last_perception_pixels = pixels
        logger.info("Supervisor's perception snapshot has been updated.")

    def _is_high_risk(self, action: str, task_context: str) -> bool:
        """
        Determines if an action is high-risk by checking its context against a
        list of sensitive keywords.
        """
        if action not in ["click", "type_text", "click_web", "type_text_web"]:
            return False

        text_to_check = task_context.lower()
        for keyword in self.high_risk_keywords:
            if keyword in text_to_check:
                logger.info(f"High-risk keyword '{keyword}' detected in task. Triggering deep validation.")
                return True

        return False

    async def approve_action(self, agent_name: str, action: str, value: any, task_context: str = "") -> bool:
        """
        The main approval function. It auto-approves low-risk actions and
        triggers deep, visual validation for high-risk ones.
        """
        logger.info(f"Received action request from '{agent_name}': {action} -> {value}")
        is_risky = self._is_high_risk(action, task_context)

        if "click" in action and is_risky:
            logger.info("High-risk click detected. Performing visual validation...")

            if self.last_perception_pixels is None:
                self.log_decision(agent_name, action, value, "No (Missing perception for high-risk action)")
                return False

            # ✅ Handle selector-based click object
            if isinstance(value, dict) and "selector" in value:
                selector = value["selector"]
                rect = await self.web_controller.find_element_js(selector)
                if not rect:
                    self.log_decision(agent_name, action, value, f"No (Selector '{selector}' not found)")
                    return False

                display_info = DisplayContext.describe()
                scale = display_info['scaling_factor']
                physical_x = rect['x'] + rect['width'] / 2
                physical_y = rect['y'] + rect['height'] / 2
                logical_x = int(physical_x / scale)
                logical_y = int(physical_y / scale)
                coords_str = f"{logical_x},{logical_y}"
            else:
                coords_str = str(value)

            is_approved, reason = self._validate_click_with_gemini(coords_str, self.last_perception_pixels, task_context)
            self.log_decision(agent_name, action, value, reason)
            return is_approved

        self.log_decision(agent_name, action, value, "Yes (Auto-approved)")
        return True

    def _validate_click_with_gemini(self, coords_str: str, pixels: np.ndarray, task_context: str) -> tuple[bool, str]:
        """
        Asks Gemini to visually confirm if a click at specific coordinates is safe and correct.
        """
        try:
            x, y = map(int, coords_str.split(','))
        except (ValueError, AttributeError):
            return False, f"Invalid coordinate format: '{coords_str}'"

        prompt = f"""
        You are a meticulous safety supervisor for an AI agent.
        The agent wants to perform a mouse click at logical coordinates (x={x}, y={y}).
        The agent's current task is: "{task_context}".

        Analyze the provided screenshot. Is there a clearly clickable and relevant UI element
        at or very near these exact coordinates?

        Respond in JSON only: {{"decision": "Yes/No", "reason": "..."}}.
        """

        response_text = smart_vision_query(pixels, prompt)
        if not response_text:
            return False, "Gemini vision query failed."

        logger.info(f"Received validation response from Gemini: {response_text}")
        try:
            match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not match:
                raise json.JSONDecodeError("No JSON object found", response_text, 0)

            parsed = json.loads(match.group(0))
            decision = parsed.get("decision", "No").lower()
            reason = parsed.get("reason", "No reason provided.")

            if decision == "yes":
                logger.info(f"Gemini approved click at ({x},{y}). Reason: {reason}")
                return True, f"Yes ({reason})"
            else:
                logger.warning(f"Gemini rejected click at ({x},{y}). Reason: {reason}")
                return False, f"No ({reason})"
        except (json.JSONDecodeError, IndexError) as e:
            logger.error(f"Failed to parse JSON from Gemini response: {e}")
            return False, f"Failed to parse validation response. Raw text: {response_text}"

    def log_decision(self, agent_name: str, action: str, value: any, response: str):
        """
        Logs the supervisor's decision for auditing and debugging purposes.
        """
        status = "approved" if "yes" in response.lower() else "blocked"
        logger.info(f"DECISION: Action '{action}' for agent '{agent_name}' -> {status.upper()}. Reason: {response}")
        self.logs.append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "action": action,
            "value": str(value),
            "response": response,
            "status": status
        })
