import asyncio
from typing import Tuple
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

class ImageInput(BaseModel):
    criteria: str
    browsing_agent_result_id: str

class ImageOutput(BaseModel):
    score: int
    reasoning: str

@default_subscription
class ImageAnalysisAgent(BaseWorker):
    """An agent that scores listings based on its images."""
    
    DEFAULT_DESCRIPTION = "A scoring assistant that scores Airbnb listings based on images scraped from the site."
    
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
            criteria, browsing_agent_result = await self._parse_context(context)
            
            listing_urls = [entry['url'] for entry in browsing_agent_result]
            image_urls = [entry['image_urls'] for entry in browsing_agent_result]
            image_outputs = await self._score_images(criteria, image_urls)
            image_agent_result = {
                listing_urls[i]: {
                    'score': image_output.score,
                    'reasoning': image_output.reasoning,
                } for i, image_output in enumerate(image_outputs)
            }

            result_id = str(uuid.uuid4())
            db = get_db()
            db.execute("INSERT INTO my_table (id, data) VALUES (?, ?)", (result_id, json.dumps(image_agent_result)))
            db.commit()
            
            response = f"Image Analysis Agent Result ID: {result_id}"
            return False, response
        
        except Exception as e:
            return False, f"Error: {str(e)}"

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
            response_format=ImageInput,
        )
        image_input = response.choices[0].message.parsed
        criteria = image_input.criteria

        browsing_agent_result_id = image_input.browsing_agent_result_id
        
        db = get_db()
        cur = db.execute("SELECT id, data FROM my_table WHERE id = ?", (browsing_agent_result_id,))
        row = cur.fetchone()
        browsing_agent_result = json.loads(row[1])
        
        return criteria, browsing_agent_result
    
    async def _score_images(self, criteria: str, image_urls: list[list[str]]) -> list[int]:
        """
        Takes in a list of lists of image URLs, each list corresponding to one listing,
        and scores the listings based on how well the images match the user's criteria.

        Args:
            criteria (str): The user's criteria for scoring.
            image_urls (list[list[str]]): A list of lists of image URLs.

        Returns:
            list[int]: A list of integers representing scores for each listing.
        """
        # Prepare the system prompt
        system_prompt = f"""
        Your task is to score an Airbnb listing based on how well the images of the listing match the user's criteria.

        User's criteria:
        {criteria}

        You will be provided the images. Output only your score as an integer from 1 to 5, 5 being the highest.
        """.strip()

        image_outputs = []

        # Iterate through each listing's image URLs
        for listing_images in image_urls:
            messages = [
                {"role": "system", "content": system_prompt},
            ]

            # Add each image URL to the messages
            for image_url in listing_images:
                messages.append(
                    {
                        "role": "user",
                        "content": "",
                        "type": "image_url",
                        "image_url": {"url": image_url},
                    }
                )

            # Call the OpenAI API
            response = await self._openai_client.beta.chat.completions.parse(
                model=MODEL_NAME,
                messages=messages,
                response_format=ImageOutput,
            )

            # Extract the score and append to the list
            image_output = response.choices[0].message.parsed
            image_outputs.append(image_output)

        return image_outputs

    async def ainput(self, prompt: str) -> str:
        """
        Simulate user input for research direction.
        
        :param prompt: Input prompt
        :return: Simulated or actual user input
        """
        return await asyncio.to_thread(input, f"{prompt} ")