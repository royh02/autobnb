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

from itertools import zip_longest
from pydantic import BaseModel
import json

class RankingInput(BaseModel):
    listings: list[str]
    description_scores: list[int]
    image_scores: list[int]

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
            context = " ".join([str(msg.content) for msg in self._chat_history[-5:]])
            listings, description_scores, image_scores = self._parse_context(context)
            ranked_listings_idxs = self._rank_listings(description_scores, image_scores)
            sorted_listings = [listings[idx] for idx in ranked_listings_idxs if idx < len(listings)]
            response = f"Here are the listings sorted by their scores: {sorted_listings}"
            return False, response
        
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    async def _parse_context(self, context: str):
        # Prepare the system prompt
        prompt = f"""
        Your task is to parse the chat history and extract a dictionary with three fields:  

        1. **listings**: A list of Airbnb URLs.
        2. **description_scores**: A list of integers for description scores.
        3. **image_scores**: A list of integers for image scores.

        Ensure all three lists have the same number of entries. If any field is missing, return an empty list for it. Ensure the lists are complete, consistent, and aligned.

        Chat history:
        {context}
        """.strip()

        # Call the OpenAI API
        response = await self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format=RankingInput,
        )

        ranking_input = response.choices[0].message.parsed
        listings = ranking_input.listings
        description_scores = ranking_input.description_scores
        image_scores = ranking_input.image_scores
        return listings, description_scores, image_scores
    
    def _rank_listings(self, description_scores: list[int], image_scores: list[int]) -> list[int]:
        weight = 0.8
        scores = [
            weight * description_score + (1 - weight) * image_score 
            for description_score, image_score in zip_longest(description_scores, image_scores, fillvalue=0)
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