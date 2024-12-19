import asyncio
from typing import Tuple
from config import MODEL_NAME, TEMPERATURE, MAX_WORKERS
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
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

class ParsingInput(BaseModel):
    criteria: str

class ParsingOutput(BaseModel):
    location: str
    checkIn: str
    checkOut: str
    additionalInfo: str
    guestsAdults: Optional[int]
    guestsChildren: Optional[int]
    guestsInfants: Optional[int]
    guestsPets: Optional[int]
    priceMin: Optional[int]
    priceMax: Optional[int]
    bedrooms: Optional[int]
    bathrooms: Optional[int]
    amenities: Optional[list[str]]

@default_subscription
class ParsingAgent(BaseWorker):
    DEFAULT_DESCRIPTION = "An agent that parses the user's preferences into a formatted dictionary to construct the URL for the start page for the search."
    
    def __init__(
        self,
        description: str = DEFAULT_DESCRIPTION,
        client = None,  # Optional model client
    ) -> None:
        super().__init__(description)
        self._openai_client = AsyncOpenAI()
    
    async def _generate_reply(self, cancellation_token: CancellationToken) -> Tuple[bool, UserContent]:
        """
        Generate a reply.
        
        :param cancellation_token: Token to check for cancellation
        :return: Tuple of (request_halt, response)
        """
        try:
            context = " ".join([str(msg.content) for msg in self._chat_history[-5:]])
            criteria = await self._parse_context(context)
            fields_dict = await self._extract_fields(criteria)
            start_url = self._format_url(fields_dict)

            # Nicely format the response
            response = "Here are the parsing outputs:\n\n"
            response += f"User's preferences: {criteria}\n"
            response += f"Starting Airbnb URL: {start_url}"
            return False, response

        except Exception as e:
            return False, f"Error: {repr(e)}"

    async def _parse_context(self, context: str) -> str:
        prompt = f"""
        Your task is to parse the chat history and extract a dictionary with one field:
        
        1. **criteria**: A string containing the user's preferences for the Airbnb they are looking for. This should be directly read from the output by the Init Agent. Be sure to include the location and check in and checkout dates if mentioned. Try to minimally modify the user's wording.

        Chat history:
        {context}
        """.strip()

        response = await self._openai_client.beta.chat.completions.parse(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            response_format=ParsingInput,
        )

        parsing_input = response.choices[0].message.parsed
        criteria = parsing_input.criteria
        return criteria

    async def _extract_fields(self, criteria: str) -> dict:
        prompt = f"""
        Extract the relevant fields from the user's preferences. Do not output any fields that are not mentioned.

        Field descriptions:
        1. location: A string containing the location the user wants the AirBNB
        2. checkIn: A string containing the check in date
        3. checkOut: A string containing the check out date
        4. guestsAdults: An int containing the number of guests that are adults
        5. guestsChildren: An int containing the number of guests that are children
        6. guestsInfants: An int containing the number of guests that are infants
        7. guestsPets: An int containing the number of guests that are pets
        8. priceMin: An string containing the minimum price of the listing the user is looking for
        9. priceMax: An string containing the maximum price of the listing the user is looking for
        10. bedrooms: An int containing the number of bedrooms the user wants
        11. bathrooms: An int containing the number of bathrooms the user wants
        12. amenities: A list of strings containing the user's requested amenities. Entries you output in this list can only be exact string matches of the following: ["WiFi", "Kitchen", "Washer", "Dryer", "Free Parking", "Gym", "Pool"]
        
        Preferences:
        {criteria}
        """.strip()
        response = await self._openai_client.beta.chat.completions.parse(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            response_format=ParsingOutput,
        )
        parsing_output = response.choices[0].message.parsed
        return parsing_output.__dict__

    def _format_url(self, data: dict) -> str:
        base_url = (
            "https://www.airbnb.com/s/"
            + data["location"]
            + "/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes"
            + "&price_filter_input_type=2"
            + "&channel=EXPLORE"
            + "&date_picker_type=calendar"
        )
        
        print("Parsed data:", data)

        url = (
            base_url
            + (f"&checkin={data['checkIn']}" if data.get("checkIn", None) else "")
            + (f"&checkout={data['checkOut']}" if data.get("checkOut", None) else "")
            + (f"&adults={data['guestsAdults']}" if data.get("guestsAdults", None) else "")
            + (f"&children={data['guestsChildren']}" if data.get("guestsChildren", None) else "")
            + (f"&infants={data['guestsInfants']}" if data.get("guestsInfants", None) else "")
            + (f"&pets={data['guestsPets']}" if data.get("guestsPets", None) else "")
            + "&source=structured_search_input_header"
            + "&search_type=filter_change"
            + "&search_mode=regular_search"
            + (f"&price_min={data['priceMin']}" if data.get("priceMin", None) else "")
            + (f"&price_max={data['priceMax']}" if data.get("priceMax", None) else "")
            + (f"&min_bedrooms={data['bedrooms']}" if data.get("bedrooms", None) else "")
            + (f"&min_bathrooms={data['bathrooms']}" if data.get("bathrooms", None) else "")
            + ("&amenities%5B%5D=4" if data.get("amenities", None) and "Wifi" in data["amenities"] else "")
            + ("&amenities%5B%5D=8" if data.get("amenities", None) and "Kitchen" in data["amenities"] else "")
            + ("&amenities%5B%5D=33" if data.get("amenities", None) and "Washer" in data["amenities"] else "")
            + ("&amenities%5B%5D=34" if data.get("amenities", None) and "Dryer" in data["amenities"] else "")
            + ("&amenities%5B%5D=9" if data.get("amenities", None) and "Free Parking" in data["amenities"] else "")
            + ("&amenities%5B%5D=15" if data.get("amenities", None) and "Gym" in data["amenities"] else "")
            + ("&amenities%5B%5D=7" if data.get("amenities", None) and "Pool" in data["amenities"] else "")
            + ("&selected_filter_order%5B%5D=pets%3A1" if data.get("guestsPets", None) else "")
        )
        return url
    
    
    async def ainput(self, prompt: str) -> str:
        """
        Simulate user input for research direction.
        
        :param prompt: Input prompt
        :return: Simulated or actual user input
        """
        return await asyncio.to_thread(input, f"{prompt} ")