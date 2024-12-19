import asyncio
from typing import Tuple
from config import MODEL_NAME, DESCRIPTION_WEIGHT, IMAGE_WEIGHT, TEMPERATURE
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
import json

class RankingInput(BaseModel):
    listings: list[str]
    description_scores: list[int]
    description_reasonings: list[str]
    image_scores: list[int]
    image_reasonings: list[str]
    criteria: str

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
                image_reasonings,
                criteria,
            ) = await self._parse_context(context)

            # Rank listings
            ranked_listings_idxs = self._rank_listings(description_scores, image_scores)
            sorted_listings = [listings[idx] for idx in ranked_listings_idxs if idx < len(listings)]
            sorted_desc_reasonings = [description_reasonings[idx] for idx in ranked_listings_idxs if idx < len(listings)]
            sorted_img_reasonings = [image_reasonings[idx] for idx in ranked_listings_idxs if idx < len(listings)]
            ranking_output = await self._summarize_reasonings(criteria, sorted_listings, sorted_desc_reasonings, sorted_img_reasonings)
            
            with open("sorted_listings.txt", "w") as file:
                for listing in sorted_listings:
                    file.write(f"{listing}\n")

            with open("sorted_listings.json", "w") as f:
                json.dump(ranking_output, f)

            response = f"Here are the listings sorted by their scores:\n{json.dumps(ranking_output, indent=2)}"
            return False, response
        
        except Exception as e:
            return False, f"Error: {repr(e)}"
    
    async def _parse_context(self, context: str):
        # Prepare the system prompt
        prompt = f"""
        Your task is to parse the chat history and extract a dictionary with six fields:  

        1. **listings**: A list of Airbnb URLs.
        2. **description_scores**: A list of integers for description scores.
        3. **description_reasonings**: A list of strings for description reasonings.
        4. **image_scores**: A list of integers for image scores.
        5. **image_reasonings**: A list of strings for image reasonings.
        6. **criteria**: A string containing the user's preferences.

        Ensure all five lists have the same number of entries. If any field is missing, return an empty list for it. Ensure the lists are complete and consistent with the chat history. Ensure that the lists are aligned such that an index in any list corresponds to the same index in any other list.

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
        criteria = ranking_input.criteria
        return listings, description_scores, description_reasonings, image_scores, image_reasonings, criteria
    
    def _rank_listings(self, description_scores: list[int], image_scores: list[int]) -> list[int]:
        scores = [
            DESCRIPTION_WEIGHT * description_score + IMAGE_WEIGHT * image_score 
            for description_score, image_score in zip_longest(description_scores, image_scores, fillvalue=0)
        ]
        sorted_listing_idxs = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        return sorted_listing_idxs

    async def _summarize_reasonings(self, criteria: str, listings: list[str], desc_analyses: list[str], img_analyses: list[str]) -> list:
        prompt_template = """
        User's preferences in looking for an Airbnb: {criteria}
        
        Analysis of the description for a found Airbnb listing: {description}
        
        Analysis of the images for a found Airbnb listing: {image}
        
        Given the above information, generate a brief summary for why this Airbnb is a good match for the user.
        """.strip()

        ranking_outputs = []
        for listing, desc_analysis, img_analysis in zip(listings, desc_analyses, img_analyses):
            prompt = prompt_template.format(
                criteria=criteria, 
                description=desc_analysis, 
                image=img_analysis
            )
            response = await self._openai_client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=TEMPERATURE
            )
            ranking_outputs.append({
                'url': listing,
                'summary': response.choices[0].message.content.strip()
            })
        return ranking_outputs

    async def ainput(self, prompt: str) -> str:
        """
        Simulate user input for research direction.
        
        :param prompt: Input prompt
        :return: Simulated or actual user input
        """
        return await asyncio.to_thread(input, f"{prompt} ")