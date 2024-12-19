import asyncio
import json
from typing import Tuple, Dict, List
from config import MODEL_NAME, TEMPERATURE, DATABASE
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
from pydantic import BaseModel
from openai import AsyncOpenAI
import uuid
import json
import sqlite3
from flask import g

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

class DescriptionInput(BaseModel):
    criteria: str
    browsing_agent_result_id: str

class DescriptionOutput(BaseModel):
    score: int
    reasoning: str

class DescriptionOutputs(BaseModel):
    outputs: list[DescriptionOutput]

@default_subscription
class DescriptionAgent(BaseWorker):
    """An agent that validates Airbnb listings against user criteria and returns scores as a list of integers 1-5."""

    DEFAULT_DESCRIPTION = """You are a validation assistant that scores Airbnb listings based on user criteria.
    You will only output a JSON array of integers corresponding to each listing's score (1-5) with no additional text."""

    def __init__(
        self,
        description: str = DEFAULT_DESCRIPTION,
        client=None,  
    ) -> None:
        super().__init__(description)
        # self._client = client
        self._openai_client = AsyncOpenAI()

    async def _generate_reply(
        self, 
        cancellation_token: CancellationToken
    ) -> Tuple[bool, UserContent]:
        """
        Generate validation scores for listings based on user criteria using a model.
        
        Args:
            listing_criteria: Dictionary containing user's search preferences
            descriptions: List of dictionaries containing found listings
            cancellation_token: Token to check for cancellation
        
        Returns:
            Tuple[bool, UserContent]: Indicates if process should halt and the validation results (as a list of integers)
        """
        # If no client is provided, return a placeholder response
        # if not self._client:
        #     return False, "No model client available. Please provide a valid client."

        try:
            context = " ".join([str(msg.content) for msg in self._chat_history])
            criteria, browsing_agent_result = await self._parse_context(context)
            
            listing_urls = [entry['url'] for entry in browsing_agent_result]
            descriptions = [entry['summary'] for entry in browsing_agent_result]
            description_outputs = await self._score_listings(criteria, descriptions)
            description_agent_result = {
                listing_urls[i]: {
                    'score': description_output.score,
                    'reasoning': description_output.reasoning,
                } for i, description_output in enumerate(description_outputs.outputs)
            }

            result_id = str(uuid.uuid4())
            db = get_db()
            db.execute("INSERT INTO my_table (id, data) VALUES (?, ?)", (result_id, json.dumps(description_agent_result)))
            db.commit()
            
            response = f"Description Agent Result ID: {result_id}"
            return False, response

        except Exception as e:
            return False, f"Error validating listings: {str(e)}"

    async def _parse_context(self, context: str):
        # Prepare the system prompt
        prompt = f"""
        Your task is to parse the chat history and extract a dictionary with two fields:  

        1. **criteria**: A string containing the user's preferences.
        2. **browsing_agent_result_id**: A string containing a uuid. This should be labeled as Browsing Agent Result ID in the chat history.

        Chat history:
        {context}
        """.strip()

        # Call the OpenAI API
        response = await self._openai_client.beta.chat.completions.parse(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            response_format=DescriptionInput,
        )
        decription_input = response.choices[0].message.parsed
        criteria = decription_input.criteria
        browsing_agent_result_id = decription_input.browsing_agent_result_id
        
        db = get_db()
        cur = db.execute("SELECT id, data FROM my_table WHERE id = ?", (browsing_agent_result_id,))
        row = cur.fetchone()
        browsing_agent_result = json.loads(row[1])
        
        return criteria, browsing_agent_result

    async def _score_listings(
        self, 
        criteria: str, 
        descriptions: List[str]
    ) -> DescriptionOutputs:
        """
        Uses a model to score the listings based on the given criteria.
        The model is instructed to return a JSON array of integers (1-5) only.

        Args:
            listing_criteria (Dict): The user's criteria
            descriptions (List[Dict]): A list of listing dictionaries

        Returns:
            List[int]: A list of integers representing scores for each listing
        """
        # Prepare the system prompt
        system_prompt = f"""
        You are a validation assistant. Given user criteria and Airbnb listings, you must:

        1. Evaluate how well each listing meets the given user criteria. Consider the user's preferences as a set of desired attributes, such as location, travel dates, the number of guests, price range, number of bedrooms and bathrooms, amenities (like a kitchen, pool, or WiFi), views (like ocean or garden views), and any additional details the user may have provided.

        For example:
        - Location: If the user wants a rental in Paris, then listings in Paris should score higher than those outside the city.
        - Travel Dates: If the user has specific check-in and check-out dates, a listing that is available for those dates should score higher than one that is not.
        - Number of Guests: If the user needs accommodation for four guests, a listing that comfortably fits four (e.g., with enough beds) should score higher than one that only fits two.
        - Price Range: If the user sets a minimum and maximum price per night, a listing that falls within that range should score higher than one that is too expensive or significantly cheaper than expected.
        - Bedrooms and Bathrooms: If the user wants two bedrooms and two bathrooms, a listing that meets or exceeds that requirement should score higher than one that does not.
        - Amenities: If the user desires certain amenities (like a fully equipped kitchen, pool, or reliable WiFi), a listing that provides these features should score higher than one that lacks them.
        - Views: If the user requests an ocean view, listings with actual ocean views should score higher than those with no view or a different view.
        - Additional Details: Consider any extra preferences, such as proximity to landmarks, pet-friendliness, or interior style. Listings that meet these details should score higher.

        Keep in mind that user criteria may be vague or broad. If the user says “affordable” without specifying a price range, consider what might be reasonable in the given context. If the user says “close to the beach,” and the listing is within walking distance, treat that as a positive match.

        2. Assign a score from 1 to 5 (5 is best) for each listing and provide a brief justification.

        User criteria:
        {criteria}
        """.strip()

        # Add listings as a user message
        listings_str = ""
        for i, listing in enumerate(descriptions, start=1):
            listings_str += f"Listing {i}:\n"
            listings_str += f"{listing}\n"
            listings_str += "\n"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": listings_str},
        ]
        response = await self._openai_client.beta.chat.completions.parse(
            model=MODEL_NAME,
            messages=messages,
            response_format=DescriptionOutputs,
        )
        return response.choices[0].message.parsed

    async def ainput(self, prompt: str) -> str:
        """Simulate user input for testing."""
        return await asyncio.to_thread(input, f"{prompt} ")