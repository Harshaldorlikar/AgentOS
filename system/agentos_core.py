# system/agentos_core.py

import logging
from tools.runtime_controller import RuntimeController

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentOSCore:
    """
    Acts as a central, stable API gateway for agents to interact with the system.
    It orchestrates requests by first seeking approval from the supervisor,
    and then executing the action via the runtime controller.
    """
    def __init__(self, supervisor):
        """
        Initializes the core with the shared supervisor instance created by the launcher.
        """
        self.supervisor = supervisor
        logger.info("AgentOSCore initialized with shared supervisor.")

    def request_action(self, agent_name: str, action_type: str, value: any, task_context: str) -> bool:
        """
        The primary method for agents to request an action.
        
        Args:
            agent_name (str): The name of the agent making the request.
            action_type (str): The type of action (e.g., 'click', 'browse').
            value (any): The target of the action (e.g., coordinates, a URL).
            task_context (str): The high-level goal the agent is trying to achieve.

        Returns:
            bool: True if the action was approved and executed, False otherwise.
        """
        # 1. Ask the supervisor for approval first.
        # The supervisor now holds the latest perception data.
        is_approved = self.supervisor.approve_action(
            agent_name=agent_name,
            action=action_type,
            value=value,
            task_context=task_context
        )

        if not is_approved:
            logger.warning(f"Supervisor blocked action '{action_type}' for agent '{agent_name}'.")
            return False

        # 2. If approved, execute the action using the RuntimeController.
        logger.info(f"Executing action '{action_type}' for agent '{agent_name}' with value: {value}")
        try:
            if action_type == "browse":
                RuntimeController.browse(value, reason=task_context)
            elif action_type == "type_text":
                RuntimeController.type_text(value, reason=task_context)
            elif action_type == "click":
                # The value is expected to be a string "x,y" from the agent
                x, y = map(int, str(value).split(','))
                RuntimeController.click(x, y, reason=task_context)
            else:
                logger.error(f"Unknown action_type requested: {action_type}")
                return False
            
            return True

        except Exception as e:
            logger.error(f"Failed to execute action '{action_type}': {e}", exc_info=True)
            return False

