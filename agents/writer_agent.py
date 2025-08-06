# agents/writer_agent.py

import os
import json
import logging
import asyncio
import random
from datetime import datetime # Re-import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from agents.agent_shell import AgentShell
from memory.memory import Memory
from system.agentos_core import AgentOSCore
from agents.supervisor import SupervisorAgent
from system.brain import Brain

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class WriterAgent(AgentShell):
    def __init__(self, core: AgentOSCore, memory: Memory, supervisor: SupervisorAgent, brain: Brain, name="WriterAgent"):
        super().__init__(name=name, core=core, memory=memory, supervisor=supervisor)
        self.brain = brain
        self.web_controller = core.web_controller
        if GEMINI_API_KEY:
            self.model = genai.GenerativeModel("gemini-1.5-pro-latest")
        else:
            self.model = None

    async def _get_tweet_variations(self, text: str) -> list:
        """Asks Gemini for a list of unique tweet variations."""
        if not self.model: return []
        
        prompt = f"""
        Analyze the following essay text. Your task is to generate 3 distinct summaries of it, each suitable for a tweet under 280 characters.
        Each version should be compelling and capture the core essence of the essay in a unique way. All tweets must end with the #PaulGraham hashtag.

        Respond with a single, valid JSON object containing a key "variations" which holds a list of the 3 tweet strings.
        Example: {{"variations": ["Tweet 1 text...", "Tweet 2 text...", "Tweet 3 text..."]}}

        Essay Text: --- {text[:4000]} ---
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            json_text = response.text[response.text.find('{'):response.text.rfind('}')+1]
            parsed_json = json.loads(json_text)
            return parsed_json.get("variations", [])
        except Exception as e:
            logger.error(f"Failed to get or parse tweet variations from Gemini: {e}")
            return []

    async def run(self):
        self.log("Starting mission: Summarize a random Paul Graham essay.")
        
        try:
            # Step 1: Perceive the page to get all available essays
            self.log("Navigating to Paul Graham's articles page...")
            await self.web_controller.browse("http://paulgraham.com/articles.html")
            await asyncio.sleep(3)
            
            self.log("Perceiving page to get all essay links...")
            dom = await self.web_controller.extract_full_dom_with_bounding_rects()
            if not dom:
                raise Exception("Could not extract DOM to find essays.")

            # Step 2: Use Python to randomly choose an essay link
            essay_links = [el for el in dom if el.get('tagName') == 'a' and el.get('text')]
            if not essay_links:
                raise Exception("Could not find any essay links on the page.")

            chosen_essay = random.choice(essay_links)
            chosen_essay_text = chosen_essay['text']
            self.log(f"Agent has randomly selected the essay: '{chosen_essay_text}'")

            # Step 3: Give the Brain a SPECIFIC mission to click the chosen essay
            mission_goal = f"Click on the link for the essay titled '{chosen_essay_text}'."
            self.log(f"Handing mission to Brain: \"{mission_goal}\"")
            success = await self.brain.run_mission(mission_goal)
            
            if not success:
                raise Exception("Brain failed its mission to click on the selected essay.")

            # Step 4: Agent resumes control to read the content
            self.log("Brain mission successful. Agent is now reading the essay content.")
            await asyncio.sleep(2)
            essay_text = await self.web_controller.get_text_content("body")
            
            if not essay_text or len(essay_text) < 500:
                raise Exception("Failed to read sufficient essay content from the page.")

            # Step 5: Get multiple tweet variations from the AI
            self.log("Asking AI for creative tweet variations...")
            tweet_variations = await self._get_tweet_variations(essay_text)
            
            if not tweet_variations:
                # Fallback if AI fails to generate variations
                raise Exception("AI failed to generate tweet variations.")

            # Step 6: Randomly choose one variation and add the timestamp for guaranteed uniqueness
            chosen_tweet = random.choice(tweet_variations)
            final_tweet = f"{chosen_tweet} [{datetime.now().strftime('%H:%M:%S')}]"

            self.log(f"Selected unique tweet for posting: \"{final_tweet}\"")
            self.memory.save("post_content", final_tweet)
            self.log("✅ Tweet saved to memory for PosterAgent.")

        except Exception as e:
            self.log(f"An error occurred during the writer's mission: {e}", level="error")
        
        self.log("WriterAgent's work is done.")