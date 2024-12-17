import asyncio
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
    """An agent that validates Airbnb listings against user criteria and provides matching scores."""

    DEFAULT_DESCRIPTION = """You are the validation agent responsible for analyzing Airbnb listings 
    and comparing them against user requirements to generate matching scores on a scale of 1-5."""

    def __init__(
        self,
        description: str = DEFAULT_DESCRIPTION,
        client=None,  # Optional client for extended functionality
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
        Generate validation scores for listings based on user criteria.
        
        Args:
            listing_criteria: Dictionary containing user's search preferences
            search_results: List of dictionaries containing found listings
            cancellation_token: Token to check for cancellation
        
        Returns:
            Tuple[bool, UserContent]: Indicates if process should halt and the validation results
        """
        try:
            validation_scores = self._validate_listing_data(listing_criteria, search_results)
            
            # Format the response with scores and explanations
            response = "Listing Match Scores:\n\n"
            for idx, score in enumerate(validation_scores):
                listing = search_results[idx]
                response += f"Listing {idx + 1}: {score}/5 stars\n"
                response += f"Location: {listing.get('Location', 'N/A')}\n"
                response += f"Price: ${listing.get('Price', 'N/A')}\n"
                response += f"Rooms: {listing.get('Number of rooms', 'N/A')}\n"
                response += f"Amenities: {', '.join(listing.get('Amenities', []))}\n\n"
            
            return False, response

        except Exception as e:
            return False, f"Error validating listings: {str(e)}"

    def _validate_listing_data(
        self, 
        listing_criteria: Dict, 
        search_results: List[Dict]
    ) -> List[int]:
        """Core validation logic that assigns scores to listings."""
        def parse_price(price_str):
            if isinstance(price_str, (int, float)):
                return float(price_str)
            if not price_str:
                return None
            return float(price_str.replace("$", ""))

        # Extract user's criteria
        user_location = listing_criteria.get("Location", "").strip()
        user_dates = listing_criteria.get("Travel dates", {})
        user_check_in = user_dates.get("Check-in", "")
        user_check_out = user_dates.get("Check-out", "")
        user_price_range = listing_criteria.get("Price range", {})
        user_min_price = parse_price(user_price_range.get("Minimum", ""))
        user_max_price = parse_price(user_price_range.get("Maximum", ""))
        user_property_type = listing_criteria.get("Property type", "").strip()
        user_rooms = listing_criteria.get("Number of rooms", "").strip()
        user_beds = listing_criteria.get("Beds", "").strip()
        user_baths = listing_criteria.get("Baths", "").strip()
        user_amenities = listing_criteria.get("Desired amenities", [])

        # Identify which criteria are active
        criteria = []
        if user_location:
            criteria.append("location")
        if user_check_in and user_check_out:
            criteria.append("dates")
        if user_min_price is not None or user_max_price is not None:
            criteria.append("price")
        if user_property_type:
            criteria.append("property_type")
        if user_rooms:
            criteria.append("rooms")
        if user_beds:
            criteria.append("beds")
        if user_baths:
            criteria.append("baths")
        if user_amenities:
            criteria.append("amenities")

        # Calculate scores for each listing
        scores = []
        if not criteria:
            return [1 for _ in search_results]

        for listing in search_results:
            matches = 0.0
            total = len(criteria)

            # Check each criterion
            if "location" in criteria:
                if listing.get("Location", "").strip().lower() == user_location.lower():
                    matches += 1

            if "price" in criteria:
                listing_price = parse_price(str(listing.get("Price", listing.get("Price range", ""))))
                if listing_price is not None:
                    if ((user_min_price is None or listing_price >= user_min_price) and 
                        (user_max_price is None or listing_price <= user_max_price)):
                        matches += 1

            if "rooms" in criteria:
                if listing.get("Number of rooms", "") == user_rooms:
                    matches += 1

            if "amenities" in criteria:
                listing_amenities = listing.get("Amenities", [])
                if user_amenities:
                    matched = sum(1 for a in user_amenities 
                                if a.lower() in [x.lower() for x in listing_amenities])
                    matches += matched / len(user_amenities)

            # Calculate final score
            ratio = matches / total if total > 0 else 0
            score = max(1, min(5, round(1 + ratio * 4)))
            scores.append(score)

        return scores

    async def ainput(self, prompt: str) -> str:
        """Simulate user input for testing."""
        return await asyncio.to_thread(input, f"{prompt} ")