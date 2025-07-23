# agents/agent_launcher.py
import sys
import os
import json
import importlib
import inspect
import logging
import asyncio
from dotenv import load_dotenv
from memory.memory import Memory
from agents.supervisor import SupervisorAgent
from system.agentos_core import AgentOSCore
from agents.agent_shell import AgentShell
from system.brain import Brain

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentLauncher:
    """
    An asynchronous launcher that can run both synchronous and asynchronous agents
    in sequence from a mission plan.
    """
    def __init__(self, mission_file: str, core: AgentOSCore, memory: Memory, supervisor: SupervisorAgent, brain: Brain):
        self.mission_file = mission_file
        self.core = core
        self.memory = memory
        self.supervisor = supervisor
        self.brain = brain
        self.agents_map = self._load_agents_map()

    def _load_agents_map(self):
        path = "agents_map.json"
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"agents_map.json not found at path: {path}")
            return {}

    def _import_agent_class(self, agent_name: str):
        module_path = self.agents_map.get(agent_name)
        if not module_path:
            logger.error(f"Module path for agent '{agent_name}' not found in agents_map.json.")
            return None
        try:
            module = importlib.import_module(module_path)
            return getattr(module, agent_name)
        except Exception as e:
            logger.error(f"Failed to import {agent_name} from {module_path}: {e}", exc_info=True)
            return None

    def _load_mission(self):
        with open(self.mission_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_mission(self, mission):
        with open(self.mission_file, "w", encoding="utf-8") as f:
            json.dump(mission, f, indent=2)

    # --- FIX: The launch_agents method is now asynchronous ---
    async def launch_agents(self):
        """
        Loads the mission and executes each step by launching the corresponding agent.
        """
        mission = self._load_mission()
        
        logger.info("Launcher starting mission execution...")

        for step in mission["steps"]:
            agent_name = step["agent"]
            task = step["task"]
            AgentClass = self._import_agent_class(agent_name)

            if not AgentClass:
                logger.warning(f"No agent class found for '{agent_name}'. Skipping.")
                step["status"] = "unavailable"
                continue

            try:
                # This correctly injects all shared dependencies into every agent it launches.
                agent_args = inspect.signature(AgentClass.__init__).parameters
                init_params = {}
                if 'memory' in agent_args: init_params['memory'] = self.memory
                if 'supervisor' in agent_args: init_params['supervisor'] = self.supervisor
                if 'core' in agent_args: init_params['core'] = self.core
                if 'brain' in agent_args: init_params['brain'] = self.brain
                if 'name' in agent_args: init_params['name'] = agent_name
                
                agent = AgentClass(**init_params)
                
                if hasattr(agent, 'task_context'):
                    agent.task_context = task

                step["status"] = "in_progress"
                self._save_mission(mission)

                logger.info(f"🚀 Launching {agent_name} for task: {task}")
                
                # --- FIX: Use 'await' for async agents, not asyncio.run() ---
                if inspect.iscoroutinefunction(agent.run):
                    logger.info(f"Detected asynchronous agent '{agent_name}'. Awaiting execution.")
                    await agent.run()
                else:
                    logger.info(f"Detected synchronous agent '{agent_name}'. Running directly.")
                    agent.run()
                
                step["status"] = "completed"

            except Exception as e:
                logger.error(f"Error running {agent_name}: {e}", exc_info=True)
                step["status"] = "error"
                step["error"] = str(e)

        self._save_mission(mission)
        logger.info("✅ Launcher has completed all mission steps.")
