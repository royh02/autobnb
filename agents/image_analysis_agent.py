import asyncio
from typing import Tuple
from autogen_core import CancellationToken, default_subscription
from autogen_core import MessageContext, TopicId
from autogen_magentic_one.messages import (
    BroadcastMessage,
    RequestReplyMessage,
    ResetMessage,
    UserContent,
)
from autogen_magentic_one.utils import message_content_to_str
from autogen_magentic_one.agents.base_worker import BaseWorker
from openai import AsyncOpenAI

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
        self._client = client
    
    async def generate_reply(self, cancellation_token: CancellationToken) -> Tuple[bool, UserContent]:
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
            criteria = ...
            image_urls = ...
            
            response = await self._score_images(criteria, image_urls)
            return False, response
        
        except Exception as e:
            return False, f"Error: {str(e)}"

    async def _score_images(criteria: str, image_urls: list[list[str]]) -> list[int]:
        """
        Takes in a list of lists of image URLs, each list corresponding to one listing,
        and scores the listings based on how well the images match the user's criteria.

        Args:
            criteria (str): The user's criteria for scoring.
            image_urls (list[list[str]]): A list of lists of image URLs.

        Returns:
            list[int]: A list of integers representing scores for each listing.
        """
        # Initialize the OpenAI client
        client = AsyncOpenAI() # TODO: set api key

        # Prepare the system prompt
        system_prompt = f"""
        Your task is to score an Airbnb listing based on how well the images of the listing match the user's criteria.

        User's criteria:
        {criteria}

        You will be provided the images. Output only your score as an integer from 1 to 5, 5 being the highest.
        """.strip()

        scores = []

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
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=10,  # Small token limit since we expect a single number as output
                temperature=0.9,
            )

            # Extract the score and append to the list
            try:
                score = int(response.choices[0].message['content'].strip())
                scores.append(score)
            except (ValueError, KeyError):
                scores.append(0)  # Default to 0 if parsing fails

        return scores

    async def ainput(self, prompt: str) -> str:
        """
        Simulate user input for research direction.
        
        :param prompt: Input prompt
        :return: Simulated or actual user input
        """
        return await asyncio.to_thread(input, f"{prompt} ")