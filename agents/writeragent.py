
from system.agentos_core import AgentOSCore
from agents.agent_shell import AgentOsCore 
from memory.memory import Memory

class WriterAgent(AgentOsCore):
    def __init__(self, name="WriterAgent"):
        super().__init__(name=name)
        self.memory = Memory()
        self.trending_topics = None

    def think(self):
        """
        The agent's thinking process. It decides to fetch trending topics.
        """
        self.log("I need to write a motivational tweet. First, I'll get the trending topics.")
        # Use AgentOSCore to request the data from the system
        self.trending_topics = AgentOSCore.request_action("get_trending_topics")
        if not self.trending_topics:
            self.log("Failed to get trending topics.", level="warning")

    def act(self):
        """
        The agent's action process. It writes and saves the tweet.
        """
        self.log("Taking action to write and save the tweet.")
        if not self.trending_topics:
            self.log("No trending topics available, cannot write a tweet.", level="error")
            # Fallback message if no topics are found
            content = "No matter what's happening in the world, your personal growth is the most important trend. Keep investing in yourself! #Motivation #PersonalGrowth"
        else:
            # Create a motivational tweet using the first trending topic
            topic = self.trending_topics[0]
            content = f"Seeing '{topic}' trending today! A great reminder that while trends come and go, your focus and determination are timeless. Make today count! #Motivation #{topic.replace(' ', '')}"

        self.log(f"Generated content: {content}")

        # Save the generated content to memory
        self.memory.save("post_content", content)
        self.log("Content saved to memory under 'post_content'.")
