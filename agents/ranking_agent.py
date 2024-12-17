import asyncio
from typing import Tuple
from autogen_core.base import CancellationToken
from autogen_core.components import default_subscription
# from autogen_core import MessageContext, TopicId
from autogen_magentic_one.messages import (
    BroadcastMessage,
    RequestReplyMessage,
    ResetMessage,
    UserContent,
)
from autogen_magentic_one.utils import message_content_to_str
from autogen_magentic_one.agents.base_worker import BaseWorker

@default_subscription
class RankingAgent(BaseWorker):
    """An agent that ranks listings based on the outputs of many scoring agents."""
    
    DEFAULT_DESCRIPTION = "A ranking assistant that ranks Airbnb listings based on the scores output by the Description Agent and Image Analysis Agent."
    
    def __init__(
        self,
        description: str = DEFAULT_DESCRIPTION,
        client = None,  # Optional model client
    ) -> None:
        super().__init__(description)
        self._client = client
    
    async def _generate_reply(self, cancellation_token: CancellationToken) -> Tuple[bool, UserContent]:
        """
        Generate a reply.
        
        :param cancellation_token: Token to check for cancellation
        :return: Tuple of (request_halt, response)
        """
        # If no client is provided, simulate a simple response
        if not self._client:
            response = "No client available. Provide a valid client."
            return False, response
        
        try:
            # Prepare context from chat history
            # context = " ".join([str(msg.content) for msg in self._chat_history[-3:]])
            listings = ...
            description_scores = ...
            image_scores = ...
            
            response = self._rank_listings(description_scores, image_scores)
            return False, response
        
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def _rank_listings(description_scores: list[int], image_scores: list[int]) -> list[int]:
        weight = 0.8
        scores = [
            weight * description_score + (1 - weight) * image_score 
            for description_score, image_score in zip(description_scores, image_scores)
        ]
        sorted_listing_idxs = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        return sorted_listing_idxs

    async def ainput(self, prompt: str) -> str:
        """
        Simulate user input for research direction.
        
        :param prompt: Input prompt
        :return: Simulated or actual user input
        """
        return await asyncio.to_thread(input, f"{prompt} ")