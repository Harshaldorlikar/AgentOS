# agents/writer_agent.py

import re
import os
import logging
from dotenv import load_dotenv
from agents.agent_shell import AgentShell
from memory.memory import Memory
import google.generativeai as genai
from system.agentos_core import AgentOSCore
from agents.supervisor import SupervisorAgent

# --- FIX: Load environment variables at the top of this module ---
# This ensures the API key is available as soon as this file is imported.
load_dotenv()

# Configure logging for this agent
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# This ensures the API key is configured before use
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("WriterAgent: GEMINI_API_KEY not found. Text generation will fail.")

class WriterAgent(AgentShell):
    """
    An autonomous agent that generates creative text content (like tweets)
    based on current trends and saves it to a shared memory space for other agents.
    """
    # --- FIX: Update __init__ to accept all shared components ---
    def __init__(self, core: AgentOSCore, memory: Memory, supervisor: SupervisorAgent, name="WriterAgent"):
        # --- FIX: Pass all shared components to the parent class ---
        super().__init__(name=name, core=core, memory=memory, supervisor=supervisor)
        self.task_context = "Write a witty, trending tweet for AgentOS."
        
        # Initialize the model once for efficiency
        if GEMINI_API_KEY:
            self.model = genai.GenerativeModel("gemini-1.5-flash-latest")
        else:
            self.model = None

    def _call_gemini_for_text(self, prompt: str) -> str | None:
        """A robust, centralized function for making text-based Gemini calls."""
        if not self.model:
            logger.error("Gemini model not initialized due to missing API key.")
            return None
        try:
            logger.info(f"Sending text prompt to Gemini: '{prompt[:50]}...'")
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini text generation failed: {e}", exc_info=True)
            return None

    def _is_english_hashtag(self, tag: str) -> bool:
        """Validates if a string is a simple English hashtag."""
        return bool(re.match(r"^#[a-zA-Z0-9_]+$", tag))

    def _get_trending_hashtags(self) -> list[str]:
        """Fetches and filters trending hashtags."""
        prompt = (
            "List 5 currently trending Twitter hashtags in India. "
            "Only include hashtags. No explanation. Separate with spaces."
        )
        response_text = self._call_gemini_for_text(prompt)
        if not response_text:
            return []
        
        raw_tags = response_text.split()
        return [tag for tag in raw_tags if self._is_english_hashtag(tag)]

    def _write_funny_tweet(self, hashtags: list[str]) -> str:
        """Writes a short, witty tweet using the provided hashtags."""
        hashtags_str = " ".join(hashtags)
        prompt = (
            f"Write a short, clever tweet using the following trending hashtags: {hashtags_str}.\n"
            f"Tone: witty, funny, sarcastic, like a clever human motivating with humor.\n"
            f"Keep under 280 characters. No emojis. Use only the given hashtags."
        )
        return self._call_gemini_for_text(prompt) or ""

    def run(self):
        """The main execution logic for the WriterAgent."""
        self.log("Fetching trending topics to write a new post...")
        
        hashtags = self._get_trending_hashtags()
        if len(hashtags) < 2:
            self.log("Not enough valid hashtags found, using fallback topics.", level="warning")
            hashtags_to_use = ["#StartupLife", "#BuildWithAI"]
        else:
            hashtags_to_use = hashtags[:2]

        self.log(f"Using hashtags: {' '.join(hashtags_to_use)}")
        
        tweet = self._write_funny_tweet(hashtags_to_use)

        # Fallback if the model fails to generate a good tweet
        if not tweet or len(tweet) < 20:
            self.log("Generated tweet was too short or empty, creating a fallback.", level="warning")
            tweet = f"Make progress, not excuses. {hashtags_to_use[0]} {hashtags_to_use[1]}"

        # Save the final content to the shared memory instance
        self.memory.save("post_content", tweet)
        self.log(f"New tweet generated: \"{tweet}\"")
        self.log("✅ Tweet saved to memory for PosterAgent.")
        self.log("Work complete. Handing off to the next agent.")

