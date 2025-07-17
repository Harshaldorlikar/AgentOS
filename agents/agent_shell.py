# agents/agent_shell.py

import os
import json
import logging
from datetime import datetime
from memory.memory import Memory
from agents.supervisor import SupervisorAgent
from system.agentos_core import AgentOSCore

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentShell:
    """
    A lightweight, dynamic base class for all agents in AgentOS.

    This shell ensures that every agent is properly initialized with shared system
    components (core, memory, supervisor) provided by the AgentLauncher.
    It provides a standardized logging utility and a simple run() method that
    child agents must override with their specific logic.
    """
    # --- FIX: The __init__ method now correctly accepts all shared components ---
    def __init__(self, name: str, core: AgentOSCore, memory: Memory, supervisor: SupervisorAgent):
        """
        Initializes the agent with shared system components.
        This constructor is designed to be called by the AgentLauncher.
        """
        self.name = name
        self.task_context = "No task assigned." # Should be set by the launcher
        
        # Use the shared instances injected by the launcher
        self.core = core
        self.memory = memory
        self.supervisor = supervisor
        
        self.log_file = f"logs/{self.name.lower()}_log.json"
        os.makedirs("logs", exist_ok=True)
        self.log(f"Agent initialized with shared core components.")

    def log(self, message: str, level: str = "info"):
        """A standardized logging method for all agents."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "level": level,
            "message": message
        }
        
        # Log to console
        console_message = f"[{self.name}] {message}"
        if level == "error":
            logger.error(console_message)
        elif level == "warning":
            logger.warning(console_message)
        else:
            logger.info(console_message)
            
        # Log to file
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

    def run(self):
        """
        The main execution entry point for the agent.
        Child classes MUST override this method with their specific logic.
        """
        # This is an abstract method. If a child agent doesn't implement it,
        # it will raise an error, which is good practice.
        raise NotImplementedError(f"The 'run' method must be implemented in the child agent: {self.name}")

