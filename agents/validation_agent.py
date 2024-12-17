import asyncio
import json
from typing import Tuple, Dict, List
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
class ListingValidationAgent(BaseWorker):
    """An agent that validates Airbnb listings against user criteria and returns scores as a list of integers 1-5."""

    DEFAULT_DESCRIPTION = """You are a validation assistant that scores Airbnb listings based on user criteria.
    You will only output a JSON array of integers corresponding to each listing's score (1-5) with no additional text."""

    def __init__(
        self,
        description: str = DEFAULT_DESCRIPTION,
        client=None,  
    ) -> None:
        super().__init__(description)
        self._client = client

    async def _generate_reply(
        self, 
        listing_criteria: Dict,
        search_results: List[Dict],
        cancellation_token: CancellationToken
    ) -> Tuple[bool, UserContent]:
        """
        Generate validation scores for listings based on user criteria using a model.
        
        Args:
            listing_criteria: Dictionary containing user's search preferences
            search_results: List of dictionaries containing found listings
            cancellation_token: Token to check for cancellation
        
        Returns:
            Tuple[bool, UserContent]: Indicates if process should halt and the validation results (as a list of integers)
        """
        # If no client is provided, return a placeholder response
        if not self._client:
            return False, "No model client available. Please provide a valid client."

        try:
            scores = await self._score_listings(listing_criteria, search_results)
            return False, str(scores)  # Convert list to string for UserContent
        except Exception as e:
            return False, f"Error validating listings: {str(e)}"

    async def _score_listings(
        self, 
        listing_criteria: Dict, 
        search_results: List[Dict]
    ) -> List[int]:
        """
        Uses a model to score the listings based on the given criteria.
        The model is instructed to return a JSON array of integers (1-5) only.

        Args:
            listing_criteria (Dict): The user's criteria
            search_results (List[Dict]): A list of listing dictionaries

        Returns:
            List[int]: A list of integers representing scores for each listing
        """
        # Prepare the system prompt
        system_prompt = f"""
        You are a validation assistant. Given user criteria and Airbnb listings, you must:

        1. Evaluate how well each listing meets the given user criteria. Consider the user’s preferences as a set of desired attributes, such as location, travel dates, the number of guests, price range, number of bedrooms and bathrooms, amenities (like a kitchen, pool, or WiFi), views (like ocean or garden views), and any additional details the user may have provided.

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

        2. Assign a score from 1 to 5 (5 is best) for each listing.

        DO NOT provide any explanations or text other than a JSON array of integers.
        For example, if there are 3 listings and their scores are 3, 5, and 2, return:
        [3,5,2]

        User criteria:
        {listing_criteria}
        """.strip()

        # Add listings as a user message
        listings_str = ""
        for i, listing in enumerate(search_results, start=1):
            listings_str += f"Listing {i}:\n"
            for k, v in listing.items():
                listings_str += f"{k}: {v}\n"
            listings_str += "\n"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": listings_str},
        ]

        response = await self._client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=messages,
            max_tokens=50,
            temperature=0.9,
        )

        # Extract response and parse as JSON
        raw_output = response.choices[0].message['content'].strip()
        try:
            scores = json.loads(raw_output)
            if not isinstance(scores, list) or not all(isinstance(s, int) for s in scores):
                raise ValueError("Model did not return a JSON list of integers.")
            return scores
        except json.JSONDecodeError:
            raise ValueError("Failed to parse model output as JSON.")

    async def ainput(self, prompt: str) -> str:
        """Simulate user input for testing."""
        return await asyncio.to_thread(input, f"{prompt} ")