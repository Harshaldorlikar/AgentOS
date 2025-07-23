# agentos.py

import sys
import os
import logging
import asyncio
from dotenv import load_dotenv

# --- This block ensures that modules can be imported correctly ---
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- Load environment variables at the very start ---
load_dotenv()

# --- Configure logging for the entire application ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Import all necessary components from your system ---
from memory.memory import Memory
from agents.supervisor import SupervisorAgent
from tools.web_controller import WebController
from system.agentos_core import AgentOSCore
from system.brain import Brain
from agents.agent_launcher import AgentLauncher

# --- The main function is now asynchronous to support Playwright ---
async def main():
    """
    The main asynchronous entry point for the AgentOS application.
    It initializes all core components and runs the mission through the launcher.
    """
    logger.info("🚀 Booting AgentOS v0.1...")
    
    web_controller = None
    try:
        # --- Step 1: Initialize Core Components ---
        # Create single, shared instances of all core system components.
        shared_memory = Memory()
        shared_supervisor = SupervisorAgent()
        
        # The WebController is a critical shared resource that needs to be managed.
        web_controller = WebController()
        
        # The core is initialized with the supervisor and web_controller.
        shared_core = AgentOSCore(supervisor=shared_supervisor, web_controller=web_controller)
        
        # --- FIX: The Brain now correctly receives the supervisor ---
        # The brain is the central cognitive engine, initialized with the core and supervisor.
        shared_brain = Brain(core=shared_core, supervisor=shared_supervisor)
        
        logger.info("✅ Core components initialized.")

        # --- Step 2: Launch the Mission via the Launcher ---
        # The launcher is now the single point of entry for all agent activities.
        launcher = AgentLauncher(
            mission_file="missions/mission_001.json", 
            core=shared_core, 
            memory=shared_memory, 
            supervisor=shared_supervisor,
            brain=shared_brain
        )
        await launcher.launch_agents()
        
        logger.info("\n✅ AgentOS mission has been completed.")

    except Exception as e:
        logger.error(f"A fatal error occurred in the main application loop: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # --- Step 3: Graceful Shutdown ---
        # Ensure the browser is always closed, even if an error occurs.
        if web_controller:
            logger.info("Shutting down web controller...")
            await web_controller.close()

if __name__ == "__main__":
    # Run the main asynchronous function
    asyncio.run(main())

