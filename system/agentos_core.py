# system/agentos_core.py

import logging
import asyncio
from tools.runtime_controller import RuntimeController
from tools.web_controller import WebController
from tools.display_context import DisplayContext
from agents.supervisor import SupervisorAgent

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentOSCore:
    """
    Acts as a central, stable API gateway for agents to interact with the system.
    It is a pure execution layer that dispatches commands from the Brain to the
    appropriate controller after they have been approved by the supervisor.
    """
    def __init__(self, supervisor: SupervisorAgent, web_controller: WebController):
        """
        Initializes the core with shared instances of the supervisor and web_controller.
        """
        self.supervisor = supervisor
        self.web_controller = web_controller
        logger.info("AgentOSCore initialized with shared components.")

    async def request_action(self, agent_name: str, action_type: str, value: any, task_context: str) -> bool:
        """
        The primary method for the Brain to command an action.
        """
        # Note: Supervisor approval is now handled by the Brain BEFORE this method is called.
        
        logger.info(f"Executing action '{action_type}' for agent '{agent_name}' with value: {value}")
        try:
            # --- Asynchronous Web Actions ---
            if action_type == "browse":
                await self.web_controller.browse(value)
            
            elif action_type == "type_text_web":
                selector = value.get("selector")
                text_to_type = value.get("text")
                await self.web_controller.type_text_in_element(selector, text_to_type)
            
            elif action_type == "click_web":
                selector = value
                # a) Use WebController for PERCEPTION (getting the coordinates)
                rect = await self.web_controller.find_element_js(selector)
                if not rect:
                    logger.error(f"Web element with selector '{selector}' not found for clicking.")
                    return False
                
                # b) Calculate the correct logical coordinates for the click
                display_info = DisplayContext.describe()
                scaling_factor = display_info['scaling_factor']
                physical_x = rect['x'] + (rect['width'] / 2)
                physical_y = rect['y'] + (rect['height'] / 2)
                logical_x = int(physical_x / scaling_factor)
                logical_y = int(physical_y / scaling_factor)
                
                # c) Use RuntimeController for EXECUTION (the physical click)
                RuntimeController.click(logical_x, logical_y, reason=f"Brain-directed click on '{selector}'")

            # --- Synchronous Desktop Actions (for other agents) ---
            elif action_type == "type_text":
                RuntimeController.type_text(value, reason=task_context)
            
            elif action_type == "click":
                x, y = map(int, str(value).split(','))
                RuntimeController.click(x, y, reason=task_context)
            
            else:
                logger.error(f"Unknown action_type requested: {action_type}")
                return False
            
            return True

        except Exception as e:
            logger.error(f"Failed to execute action '{action_type}': {e}", exc_info=True)
            return False
