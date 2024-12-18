import asyncio
from typing import Tuple
from config import MODEL_NAME, DESCRIPTION_WEIGHT, IMAGE_WEIGHT
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
from openai import AsyncOpenAI

class RankingInput(BaseModel):
    listings: list[str]
    description_scores: list[int]
    description_reasonings: list[str]
    image_scores: list[int]
    image_reasonings: list[str]

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
        # self._client = client
        self._openai_client = AsyncOpenAI()
    
    async def _generate_reply(self, cancellation_token: CancellationToken) -> Tuple[bool, UserContent]:
        """
        Generate a reply.
        
        :param cancellation_token: Token to check for cancellation
        :return: Tuple of (request_halt, response)
        """
        # If no client is provided, simulate a simple response
        # if not self._client:
        #     response = "No client available. Provide a valid client."
        #     return False, response

        try:
            # Prepare context from chat history
            context = " ".join([str(msg.content) for msg in self._chat_history])
            (
                listings,
                description_scores,
                description_reasonings,
                image_scores,
                image_reasonings
            ) = await self._parse_context(context)

            # Rank listings
            ranked_listings_idxs = self._rank_listings(description_scores, image_scores)
            sorted_listings = [listings[idx] for idx in ranked_listings_idxs if idx < len(listings)]
            response = f"Here are the listings sorted by their scores: {sorted_listings}"

            # TODO: Generate ranking summaries
            with open("sorted_listings.txt", "w") as file:
                for listing in sorted_listings:
                    file.write(f"{listing}\n")

            return False, response
        
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    async def _parse_context(self, context: str):
        # Prepare the system prompt
        prompt = f"""
        Your task is to parse the chat history and extract a dictionary with five fields:  

        1. **listings**: A list of Airbnb URLs.
        2. **description_scores**: A list of integers for description scores.
        3. **description_reasonings**: A list of strings for description reasonings.
        4. **image_scores**: A list of integers for image scores.
        5. **image_reasonings**: A list of strings for image reasonings.

        Ensure all three lists have the same number of entries. If any field is missing, return an empty list for it. Ensure the lists are complete and consistent with the chat history. Ensure that the lists are aligned such that an index in any list corresponds to the same index in any other list.

        Chat history:
        {context}
        """.strip()

        # Call the OpenAI API
        response = await self._openai_client.beta.chat.completions.parse(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            response_format=RankingInput,
        )

        ranking_input = response.choices[0].message.parsed
        listings = ranking_input.listings
        description_scores = ranking_input.description_scores
        description_reasonings = ranking_input.description_reasonings
        image_scores = ranking_input.image_scores
        image_reasonings = ranking_input.image_reasonings
        return listings, description_scores, description_reasonings, image_scores, image_reasonings
    
    def _rank_listings(self, description_scores: list[int], image_scores: list[int]) -> list[int]:
        scores = [
            DESCRIPTION_WEIGHT * description_score + IMAGE_WEIGHT * image_score 
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