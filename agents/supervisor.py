# agents/supervisor.py

import json
import logging
import re # ✅ Import regular expressions
from datetime import datetime
import numpy as np
from tools.gemini_ui_vision import smart_vision_query

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SupervisorAgent:
    """
    Acts as a selective safety and validation layer for other agents.
    It intervenes only on high-risk actions.
    """
    def __init__(self):
        self.logs = []
        self.last_perception_pixels = None
        self.high_risk_keywords = [
            "post", "delete", "confirm", "purchase", "send", "submit", 
            "login", "password", "credentials", "pay", "buy", "approve"
        ]

    def update_perception(self, pixels: np.ndarray):
        """Stores the latest visual snapshot (pixel array) from an agent."""
        self.last_perception_pixels = pixels
        logger.info("Updated perception snapshot stored.")

    def _is_high_risk(self, action: str, value: any, task_context: str) -> bool:
        """Determines if an action is high-risk."""
        if action not in ["click", "type_text"]:
            return False

        combined_text = (str(task_context) + " " + str(value)).lower()
        for keyword in self.high_risk_keywords:
            if keyword in combined_text:
                logger.info(f"High-risk keyword '{keyword}' detected. Triggering deep validation.")
                return True
        return False

    def approve_action(self, agent_name: str, action: str, value: any, task_context: str = "") -> bool:
        """The main approval function for all agent actions."""
        logger.info(f"Received action request from '{agent_name}': {action} -> {value}")
        is_risky = self._is_high_risk(action, value, task_context)

        if action == "click":
            if is_risky:
                logger.info("Action is high-risk. Performing visual validation...")
                if self.last_perception_pixels is None:
                    self.log_decision(agent_name, action, value, "No (Missing perception for high-risk action)")
                    return False
                is_approved, reason = self._validate_click_with_gemini(value, self.last_perception_pixels, task_context)
                self.log_decision(agent_name, action, value, reason)
                return is_approved
            else:
                self.log_decision(agent_name, action, value, "Yes (Low-risk click, auto-approved)")
                return True
        
        # For now, all typing actions are approved after a basic content check.
        # This could be expanded with visual validation for high-risk typing.
        elif action == "type_text":
            if not isinstance(value, str) or len(value.strip()) < 3:
                self.log_decision(agent_name, action, value, "No (Invalid content)")
                return False
            self.log_decision(agent_name, action, value, "Yes (Content validated)")
            return True

        elif action in ["browse", "open_app"]:
            self.log_decision(agent_name, action, value, "Yes (Safe default approval)")
            return True
        
        self.log_decision(agent_name, action, value, "No (Unknown action type)")
        return False

    def _validate_click_with_gemini(self, coords_str: str, pixels: np.ndarray, task_context: str) -> tuple[bool, str]:
        """Asks Gemini to visually confirm if a click is safe and correct."""
        try:
            x, y = map(int, coords_str.split(','))
        except (ValueError, AttributeError):
            return False, f"Invalid coords format: '{coords_str}'"

        prompt = f"""You are a meticulous safety supervisor for an AI agent. The agent wants to perform a mouse click at the logical coordinates (x={x}, y={y}). The agent's current task is: "{task_context}". Analyze the provided screenshot. Is there a clearly clickable and relevant UI element at or very near these exact coordinates? Respond with a single word and a brief reason in JSON format: {{"decision": "Yes/No", "reason": "..."}}"""
        
        response_text = smart_vision_query(pixels, prompt)
        if not response_text:
            return False, "Gemini vision query failed."

        logger.info(f"Received validation response from Gemini: {response_text}")

        try:
            # --- FIX: Use a regular expression to robustly find the JSON object ---
            # This handles cases where the model wraps the JSON in markdown fences.
            match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not match:
                raise json.JSONDecodeError("No JSON object found in response", response_text, 0)
            
            json_string = match.group(0)
            parsed = json.loads(json_string)
            decision = parsed.get("decision", "No").lower()
            reason = parsed.get("reason", "No reason provided.")
            
            if decision == "yes":
                logger.info(f"Gemini approved click at ({x},{y}). Reason: {reason}")
                return True, f"Yes ({reason})"
            else:
                logger.warning(f"Gemini rejected click at ({x},{y}). Reason: {reason}")
                return False, f"No ({reason})"
        except (json.JSONDecodeError, IndexError) as e:
            logger.error(f"Failed to parse JSON from Gemini validation response: {e}")
            return False, f"Failed to parse validation response. Raw text: {response_text}"

    def log_decision(self, agent_name: str, action: str, value: any, response: str):
        """Logs the supervisor's decision for auditing."""
        status = "approved" if "yes" in response.lower() else "blocked"
        logger.info(f"DECISION: Action '{action}' for agent '{agent_name}' -> {status.upper()}. Reason: {response}")
        self.logs.append({"timestamp": datetime.now().isoformat(), "agent": agent_name, "action": action, "value": str(value), "response": response, "status": status})
