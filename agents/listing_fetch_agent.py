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
<<<<<<< HEAD
from openai import AsyncOpenAI
=======
from playwright.sync_api import sync_playwright
>>>>>>> ab9694b (fix listing)


def get_dynamic_html(url):
    try:
        # Start Playwright and open the browser
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)  # Set headless=False if you want to see the browser
            page = browser.new_page()
            # Go to the page
            page.goto(url)
            # Wait for the page to load completely
            page.wait_for_load_state('networkidle')
            # Get the final HTML after JavaScript has executed
            html_content = page.content()

            browser.close()
            return html_content

    except Exception as e:
        return f"Error fetching page: {e}"


# Function to extract Airbnb listing links
def extract_airbnb_listing_links(url):
    try:
        # Step 1: Fetch HTML content from the Airbnb page
        html_content = get_dynamic_html(url)
        
        # Step 2: Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Step 3: Find all `<a>` tags and filter for listing links
        base_url = "https://www.airbnb.com"  # Base URL for constructing full links
        listings = []
        for a_tag in soup.find_all('a', href=True, recursive=True):
            href = a_tag['href']
            print(href)
            if "/rooms/" in href:  # Airbnb listing URLs usually contain '/rooms/'
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
        Your task is to parse the chat history and extract a string containing the URL of the Airbnb website. Output only the url.

        Chat history:
        {context}
        """.strip()

        # Call the OpenAI API
        response = await self._openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )

        extracted_url = response.choices[0].message.content.strip()
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