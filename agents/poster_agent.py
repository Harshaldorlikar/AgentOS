# agents/poster_agent.py

import logging
import asyncio
from agents.agent_shell import AgentShell
from system.brain import Brain
from system.agentos_core import AgentOSCore
from agents.supervisor import SupervisorAgent
from memory.memory import Memory

# Configure logging for this agent
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PosterAgent(AgentShell):
    """
    An agent whose sole responsibility is to post content to X (Twitter).
    In the final architecture, it achieves this by defining a high-level goal
    and delegating the entire execution to the central Brain.
    """
    def __init__(self, core: AgentOSCore, memory: Memory, supervisor: SupervisorAgent, brain: Brain, name="PosterAgent"):
        """
        Initializes the PosterAgent with all shared system components, including the Brain.
        """
        super().__init__(name=name, core=core, memory=memory, supervisor=supervisor)
        self.brain = brain # Store the shared brain instance

    async def run(self):
        """
        The main execution logic for the PosterAgent. It defines the goal and
        invokes the Brain to run the mission autonomously.
        """
        self.log(f"Agent '{self.name}' is running.")

        # 1. Load the necessary information from shared memory.
        content_to_post = self.memory.load("post_content")
        if not content_to_post:
            self.log("No post content found in memory. Aborting mission.", level="error")
            return

        # 2. Define the high-level goal for the Brain in clear, natural language.
        mission_goal = (
            f"Navigate to the X.com compose page, type the following tweet into the main text area, "
            f"and then click the final 'Post' button to publish it: \"{content_to_post}\""
        )
        self.log(f"Defined mission goal for the Brain: {mission_goal}")

        # 3. Delegate the entire mission to the Brain.
        # The Brain will now handle the entire perceive-think-act loop, including
        # navigation, typing, clicking, and verifying success.
        await self.brain.run_mission(mission_goal)

        self.log("Brain has completed the mission. PosterAgent's work is done.")

