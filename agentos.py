# agentos.py

import sys
import os
import logging
from dotenv import load_dotenv

# --- FIX: Add this block to correctly set up the Python path ---
# This ensures that modules can be imported correctly from anywhere in the project.
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- FIX: Load environment variables at the very start ---
# This is crucial for the API keys to be available to all modules.
load_dotenv()

# Configure logging for the entire application
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Import all necessary components from your system ---
from memory.memory import Memory
from agents.supervisor import SupervisorAgent
from system.agentos_core import AgentOSCore
from agents.director_agent import DirectorAgent
from agents.dev_agent import DevAgent
from agents.agent_launcher import AgentLauncher
from system.system_brain import SystemBrainAgent
from system.self_patcher import SelfPatcherAgent

def main():
    """
    The main entry point and boot sequence for the AgentOS application.
    It initializes all core components and runs agents in a structured order.
    """
    logger.info("🚀 Booting AgentOS v0.1...")

    try:
        # --- Step 1: Initialize Core Components ---
        # Create single, shared instances of memory, supervisor, and the core.
        # These will be passed to all agents to ensure they work together.
        shared_memory = Memory()
        shared_supervisor = SupervisorAgent()
        shared_core = AgentOSCore(supervisor=shared_supervisor)
        logger.info("✅ Core components initialized.")

        # --- Step 2: Launch Director Agent ---
        # The Director interacts with the user to define the mission.
        logger.info("\n🎬 Launching DirectorAgent...")
        director = DirectorAgent(core=shared_core, memory=shared_memory, supervisor=shared_supervisor)
        director.run()

        # --- Step 3: Run DevAgent ---
        # The DevAgent acts on the user's goal to potentially create new agents.
        logger.info("\n💻 Running DevAgent to build agents from goal...")
        dev_agent = DevAgent(core=shared_core, memory=shared_memory, supervisor=shared_supervisor)
        dev_agent.run()

        # --- Step 4: Launch Task Agents via Launcher ---
        # The launcher reads the mission file created by the Director and executes the steps.
        logger.info("\n🚀 Launching agents as per mission plan...")
        # The launcher now gets the shared components to pass them to the agents it creates.
        launcher = AgentLauncher(mission_file="missions/mission_001.json", core=shared_core, memory=shared_memory, supervisor=shared_supervisor)
        launcher.launch_agents()

        # --- Step 5: Run System Maintenance Agents ---
        # These agents can reflect on the mission's execution.
        logger.info("\n🔬 Running system maintenance agents...")
        # Note: These agents also need to be updated to accept the shared components.
        system_brain = SystemBrainAgent(core=shared_core, memory=shared_memory, supervisor=shared_supervisor)
        system_brain.run()
        
        patcher = SelfPatcherAgent(core=shared_core, memory=shared_memory, supervisor=shared_supervisor)
        patcher.run()

        logger.info("\n✅ AgentOS mission has been completed.")

    except Exception as e:
        logger.error(f"A fatal error occurred in the main application loop: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
