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

class BrowsingInput(BaseModel):
    listing_urls: list[str]

@default_subscription
class BrowsingAgent(BaseWorker):
    """An agent that visits URLs provided by the Listing Fetch Agent and generates a summary of each listing."""
    DEFAULT_DESCRIPTION = "An agent that visits URLs provided by the Listing Fetch Agent and generates a summary of each listing."
    
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
            listing_urls = await self._parse_context(context)
            scraped_listings = await self._scrape_listings(listing_urls)
            
            # Nicely format the response
            response = "Here are the scraped listings:\n\n"
            for scraped_listing in scraped_listings:
                response += f"URL:{scraped_listing['url']}\n"
                response += f"Summary:{scraped_listing['summary']}\n"
                response += f"Image URLs:\n"
                for image_url in scraped_listing['image_urls']:
                    response += f"    {image_url}\n"
                response += "\n"
            return False, response

        except Exception as e:
            return False, f"Error: {str(e)}"

    async def _parse_context(self, context: str):
        prompt = f"""
        Your task is to parse the chat history and extract a dictionary with one field:
        
        1. **listing_urls**: A list of every url returned by the Listing Fetch Agent.

        If the field is missing, return an empty list for it. Ensure the list is complete and consistent with the chat history.

        Chat history:
        {context}
        """.strip()

        response = await self._openai_client.beta.chat.completions.parse(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            response_format=BrowsingInput,
        )

        browsing_input = response.choices[0].message.parsed
        listing_urls = browsing_input.listing_urls
        return listing_urls
    
    async def _scrape_listings(self, listing_urls: list[str]) -> list[dict]:
        async def get_listing_content(url: str) -> dict:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url)
                await page.wait_for_load_state('networkidle')
                html_content = await page.content()
                await browser.close()

            soup = BeautifulSoup(html_content, 'html.parser')

            # Remove unnecessary tags
            for tag in soup(["script", "style", "noscript", "meta", "link"]):
                tag.decompose()

            clean_text = soup.get_text(separator="\n", strip=True)

            # Extract images (preserve 'src' attributes)
            images = []
            for img in soup.find_all("img"):
                src = img.get("src")
                if src and src.startswith("http"):  # Filter for valid URLs
                    images.append(src)

            listing_content = {
                "text": clean_text,
                "images": images
            }

            return listing_content

        async def content_to_summary(listing_text: str) -> str:
            system_prompt = "Given HTML of an Airbnb listing, write a summary of the contents of the page, including all details about the listing such that the summary will be easily ingestible for a downstream AI to analyze in terms of matching user preferences."

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": listing_text},
            ]
            response = await self._openai_client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=TEMPERATURE,
            )
            summary = response.choices[0].message.content.strip()
            return summary

        async def summarize_listing(url):
            listing_content = await get_listing_content(url)
            summary = await content_to_summary(listing_content['text'])
            return {
                "url": url,
                "summary": summary,
                "image_urls": listing_content['images']
            }

        results = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(executor, asyncio.run, summarize_listing(url))
                for url in listing_urls
            ]
            for task in asyncio.as_completed(tasks):
                try:
                    result = await task
                    results.append(result)
                except Exception as e:
                    print(f"Error summarizing listing: {e}, skipping this one...")
        return results

    async def ainput(self, prompt: str) -> str:
        """
        Simulate user input for research direction.
        
        :param prompt: Input prompt
        :return: Simulated or actual user input
        """
        return await asyncio.to_thread(input, f"{prompt} ")