import asyncio
from typing import Tuple
from config import MODEL_NAME, DESCRIPTION_WEIGHT, IMAGE_WEIGHT, TEMPERATURE, DATABASE, SHOWN_LISTING_COUNT
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
import uuid
import sqlite3
from flask import g

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

class RankingInput(BaseModel):
    criteria: str
    description_agent_result_id: str
    image_agent_result_id: str
    final_result_id: str

@default_subscription
class RankingAgent(BaseWorker):
    DEFAULT_DESCRIPTION = "A agent that ranks Airbnb listings based on the scores output by the Description Agent and Image Analysis Agent."
    
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
                criteria,
                description_agent_result,
                image_agent_result,
                final_result_id,
            ) = await self._parse_context(context)

            listing_urls = list(set(list(description_agent_result.keys()) + list(image_agent_result.keys())))
            listings = []
            description_scores = []
            description_reasonings = []
            image_scores = []
            image_reasonings = []
            for url in listing_urls:
                if url in description_agent_result and url in image_agent_result:
                    listings.append(url)
                    description_scores.append(description_agent_result[url]['score'])
                    description_reasonings.append(description_agent_result[url]['reasoning'])
                    image_scores.append(image_agent_result[url]['score'])
                    image_reasonings.append(image_agent_result[url]['reasoning'])

            # Rank listings
            ranked_listings_idxs = self._rank_listings(description_scores, image_scores)
            sorted_listings = [listings[idx] for idx in ranked_listings_idxs if idx < len(listings)]
            sorted_desc_reasonings = [description_reasonings[idx] for idx in ranked_listings_idxs if idx < len(listings)]
            sorted_img_reasonings = [image_reasonings[idx] for idx in ranked_listings_idxs if idx < len(listings)]
            ranking_output = await self._summarize_reasonings(criteria, sorted_listings, sorted_desc_reasonings, sorted_img_reasonings)
            ranking_output = ranking_output[:SHOWN_LISTING_COUNT]

            db = get_db()
            db.execute("INSERT INTO my_table (id, data) VALUES (?, ?)", (final_result_id, json.dumps(ranking_output)))
            db.commit()

            response = f"I have sent the sorted listings to the user. The request is satisfied."
            return False, response
        
        except Exception as e:
            return False, f"Error: {repr(e)}"
    
    async def _parse_context(self, context: str):
        # Prepare the system prompt
        prompt = f"""
        Your task is to parse the chat history and extract a dictionary with four fields:  

        1. **criteria**: A string containing the user's preferences.
        2. **description_agent_result_id**: A string containing a uuid. This should be labeled as Description Agent Result ID in the chat history.
        3. **image_agent_result_id**: A string containing a uuid. This should be labeled as Image Analysis Agent Result ID in the chat history.
        4. **final_result_id**: A string containing a uuid. This should be labeled as Final Result ID in the chat history.

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
        criteria = ranking_input.criteria
        description_agent_result_id = ranking_input.description_agent_result_id
        image_agent_result_id = ranking_input.image_agent_result_id
        final_result_id = ranking_input.final_result_id
        
        db = get_db()
        cur = db.execute("SELECT id, data FROM my_table WHERE id = ?", (description_agent_result_id,))
        row = cur.fetchone()
        description_agent_result = json.loads(row[1])
        cur = db.execute("SELECT id, data FROM my_table WHERE id = ?", (image_agent_result_id,))
        row = cur.fetchone()
        image_agent_result = json.loads(row[1])
        return criteria, description_agent_result, image_agent_result, final_result_id
    
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