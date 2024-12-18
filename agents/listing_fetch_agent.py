import asyncio
from typing import Tuple, Dict
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
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from openai import AsyncOpenAI

def extract_airbnb_listing_links(url):
    try:
        # Step 1: Fetch HTML content from the Airbnb page
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text
        
        # Step 2: Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Step 3: Find all `<a>` tags and filter for listing links
        base_url = "https://www.airbnb.com"  # Base URL for constructing full links
        listings = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if "/rooms/" in href:  # Listing URLs contain '/rooms/'
                full_url = urljoin(base_url, href)  # Construct full URL
                listings.append(full_url)
        
        # Step 4: Format and output the result
        formatted_list = [
            f"{i + 1}. {url}" for i, url in enumerate(listings)
        ]
        return "\n\n".join(formatted_list)
    except requests.exceptions.RequestException as e:
        return f"Error fetching page: {e}"
    except Exception as e:
        return f"Error processing HTML: {e}"

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
        self._openai_client = AsyncOpenAI()

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
            
            # response = """
            # Given a URL link with the inputted search criteria, retrive a list of hyperlinks containing each individual listing.
            # Use the helper function extract_airbnb_listing_links(url) and replace url with the corresponding URL.

            # Simply output the list in the format below.

            # 1. [URL]
            # 2. [URL]
            # ...

            # """
            # Prepare context from chat history
            context = " ".join([str(msg.content) for msg in self._chat_history[-5:]])
            extracted_url = await self._parse_context(context)
            listing_urls = extract_airbnb_listing_links(extracted_url)
            response = f"Here are the listing urls: {listing_urls}"
            return False, response


        except Exception as e:
            return False, f"Error fetching listings: {str(e)}"

    async def _parse_context(self, context: str):
        # Prepare the system prompt
        prompt = f"""
        Your task is to parse the chat history and extract a string containing the URL of the Airbnb website.

        Chat history:
        {context}
        """.strip()

        # Call the OpenAI API
        response = await self._openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )

        extracted_url = response.choices[0].message['content'].strip()
        return extracted_url 

    async def ainput(self, prompt: str) -> str:
        """
        Simulate user input for custom responses.

        Args:
            prompt (str): Input prompt for user

        Returns:
            str: User's response (simulated or actual)
        """
        return await asyncio.to_thread(input, f"{prompt} ")