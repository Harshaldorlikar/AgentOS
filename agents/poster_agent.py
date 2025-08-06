# agents/poster_agent.py

import logging
import asyncio
from agents.agent_shell import AgentShell
from system.brain import Brain
from system.agentos_core import AgentOSCore
from agents.supervisor import SupervisorAgent
from memory.memory import Memory

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PosterAgent(AgentShell):
    def __init__(self, core: AgentOSCore, memory: Memory, supervisor: SupervisorAgent, brain: Brain, name="PosterAgent"):
        super().__init__(name=name, core=core, memory=memory, supervisor=supervisor)
        self.brain = brain
        # NEW: Add a direct reference to the web_controller for agent-led actions.
        self.web_controller = core.web_controller

    # MODIFIED: The run method now separates navigation from the Brain's main task for reliability.
    async def run(self):
        self.log(f"Agent '{self.name}' is running.")
        content_to_post = self.memory.load("post_content")
        if not content_to_post:
            self.log("No post content found in memory. Aborting mission.", level="error")
            return

        try:
            # Step 1: Agent handles the navigation directly. This is unambiguous.
            self.log("Agent is now navigating to the X.com compose page...")
            await self.web_controller.browse("https://x.com/compose/post")
            self.log("Waiting for the page to load completely...")
            await asyncio.sleep(7) # A generous wait for the dynamic UI

            # Step 2: Agent gives the Brain a simpler, more focused mission.
            # The Brain is now starting on the correct page.
            mission_goal = (
                f"Type the following tweet into the main text area, "
                f"click the final 'Post' button to publish it, and then verify it was posted before finishing. "
                f"Tweet content: \"{content_to_post}\""
            )
            self.log(f"Handing focused mission to Brain: {mission_goal}")

            # Step 3: Delegate the focused mission to the Brain and check for success.
            success = await self.brain.run_mission(mission_goal)
            
            if success:
                self.log("✅ DEMO COMPLETE! Brain has successfully posted the tweet.")
            else:
                self.log("Mission failed. The Brain was unable to complete the posting process.", level="error")

        except Exception as e:
            self.log(f"A critical error occurred in the PosterAgent's mission: {e}", level="error")

        self.log("PosterAgent's work is done.")