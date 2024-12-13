import asyncio
from typing import Tuple, Dict
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

# def fetch_listings_data(user_prompt: str) -> Dict[str, str]:
#     """
#     This function takes in a user prompt for listing search features and identifies the key filters for fetching Airbnb listings.
#     Converts textual dates into numerical formats (YYYY-MM-DD).

#     Args:
#         user_prompt (str): The user's input describing their desired listing features.
    
#     Returns:
#         Dict[str, str]: A dictionary with the identified filters, or blanks if not specified.

#     The listing fetch agent should have access to this function signature, and it should be able to suggest this as a function call.

#     Example:
#     > user_prompt = "
#         I want to go to New York for vacation. My travel dates are from December 20, 2024, to December 27, 2024. 
#         I'd like to spend no more than $500 per night. I'm looking for a property with three bedrooms, 
#         and I really want amenities like a back patio for barbeques and a pool.
#         "
#     > fetch_listings_data(user_prompt)
#     {
#         "Location": "New York",
#         "Travel dates": {"Check-in": "2024-12-20", "Check-out": "2024-12-27"},
#         "Price range": {"Minimum": "", "Maximum": "$500"},
#         "Property type": "",
#         "Number of rooms": "3",
#         "Beds": "",
#         "Baths": "",
#         "Desired amenities": ["Back patio for barbeque", "Pool"],
#     }
#     """
#     search_filters = {
#         "Location": "",
#         "Travel dates": {"Check-in": "", "Check-out": ""},
#         "Price range": {"Minimum": "", "Maximum": ""},
#         "Property type": "",
#         "Number of rooms": "",
#         "Beds": "",
#         "Baths": "",
#         "Desired amenities": [],
#     }

#     lines = user_prompt.split('\n')
#     for line in lines:
#         lower_line = line.lower()
#         if "location" in lower_line:
#             search_filters["Location"] = line.split(":")[-1].strip()
#         elif "check-in" in lower_line or "check-out" in lower_line:
#             if "check-in" in lower_line:
#                 date = line.split(":")[-1].strip()
#                 search_filters["Travel dates"]["Check-in"] = date
#             if "check-out" in lower_line:
#                 date = line.split(":")[-1].strip()
#                 search_filters["Travel dates"]["Check-out"] = date
#         elif "price range" in lower_line or "price" in lower_line:
#             if "min" in lower_line:
#                 search_filters["Price range"]["Minimum"] = line.split(":")[-1].strip()
#             if "max" in lower_line:
#                 search_filters["Price range"]["Maximum"] = line.split(":")[-1].strip()
#         elif "property type" in lower_line:
#             search_filters["Property type"] = line.split(":")[-1].strip()
#         elif "rooms" in lower_line:
#             search_filters["Number of rooms"] = line.split(":")[-1].strip()
#         elif "beds" in lower_line:
#             search_filters["Beds"] = line.split(":")[-1].strip()
#         elif "baths" in lower_line:
#             search_filters["Baths"] = line.split(":")[-1].strip()
#         elif "amenities" in lower_line or "amenity" in lower_line:
#             amenities = line.split(":")[-1].strip()
#             search_filters["Desired amenities"] = [a.strip() for a in amenities.split(",")]

#     return search_filters

@default_subscription
class ListingFetchAgent(BaseWorker):
    """An agent that processes user input and fetches Airbnb listings."""

    DEFAULT_DESCRIPTION = """You are an intelligent agent designed to fetch listings on the current page.
    Display results with a hyperlink to each relevant Airbnb listing."""

    def __init__(
        self,
        description: str = DEFAULT_DESCRIPTION,
        client=None,  # Optional client for extended functionality
    ) -> None:
        super().__init__(description)
        self._client = client

    async def _generate_reply(self, cancellation_token: CancellationToken) -> Tuple[bool, UserContent]:
        """
        Generate a reply based on user input to fetch listings data.

        Args:
            cancellation_token (CancellationToken): Token to check for cancellation

        Returns:
            Tuple[bool, UserContent]: Indicates if the process should halt and the generated content.
        """
        try:
            # Get the latest user prompt from chat history
            
            response = """
            Given a list of the following listings, retrieve a hyperlink for each listing and output a numbered list with titles and clickable hyperlinks.
            Make sure to gather the listings of at least 3 pages. Do not click into each individual hyperlink. Simply output the list in the format below.

            1. [Title of Result 1]  
            Link: [URL]

            2. [Title of Result 2]  
            Link: [URL]
            ...

            """
            return False, response

        except Exception as e:
            return False, f"Error fetching listings: {str(e)}"

    async def ainput(self, prompt: str) -> str:
        """
        Simulate user input for custom responses.

        Args:
            prompt (str): Input prompt for user

        Returns:
            str: User's response (simulated or actual)
        """
        return await asyncio.to_thread(input, f"{prompt} ")