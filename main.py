import asyncio
import logging
import os
import argparse
import json

from autogen_core import SingleThreadedAgentRuntime
from autogen_core.application.logging import EVENT_LOGGER_NAME
from autogen_core.base import AgentId, AgentProxy, Subscription
from autogen_core.models._types import UserMessage
from autogen_magentic_one.agents.multimodal_web_surfer import MultimodalWebSurfer
from autogen_magentic_one.agents.orchestrator import LedgerOrchestrator
from autogen_magentic_one.agents.user_proxy import UserProxy
from autogen_magentic_one.messages import BroadcastMessage, RequestReplyMessage
from autogen_magentic_one.utils import LogHandler, create_completion_client_from_env
from openai import OpenAI
from agents.init_agent import InitAgent
from agents.browsing_agent import BrowsingAgent
from agents.listing_fetch_agent import ListingFetchAgent
from agents.image_analysis_agent import ImageAnalysisAgent
from agents.ranking_agent import RankingAgent
from agents.description_agent import DescriptionAgent
from agents.parsing_agent import ParsingAgent
from config import MODEL_NAME, MAX_LISTING_COUNT, FLASK_PORT, DATABASE

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import asyncio
import os
import tempfile
from urllib.parse import unquote
import time
from playwright.sync_api import sync_playwright
import requests
from bs4 import BeautifulSoup
import sqlite3
from flask import g

app = Flask(__name__)
cors = CORS(app)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.executescript(f.read())

# Create a cache directory for screenshots
CACHE_DIR = os.path.join(tempfile.gettempdir(), 'airbnb_previews')
os.makedirs(CACHE_DIR, exist_ok=True)

def get_image_url(url):
    try:
        # Set up headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch the page content
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to find the meta image tag
        meta_image = soup.find('meta', {'itemprop': 'image'})
        if meta_image and meta_image.get('content'):
            return meta_image['content']
            
        # Fallback: try other meta tags
        meta_og_image = soup.find('meta', {'property': 'og:image'})
        if meta_og_image and meta_og_image.get('content'):
            return meta_og_image['content']
            
        return None
    except Exception as e:
        print(f"Error getting image URL: {str(e)}")
        return None

def get_screenshot(url):
    # Create a cache filename based on the URL
    cache_file = os.path.join(CACHE_DIR, f"{hash(url)}.png")
    
    # Check if cached version exists and is less than 24 hours old
    if os.path.exists(cache_file):
        file_age = time.time() - os.path.getmtime(cache_file)
        if file_age < 86400:  # 24 hours in seconds
            return cache_file

    # Get the image URL from the page
    image_url = get_image_url(url)
    if not image_url:
        print(f"No image URL found for {url}")
        return None

    # Download and save the image
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(image_url, headers=headers)
        if response.status_code == 200:
            with open(cache_file, 'wb') as f:
                f.write(response.content)
            return cache_file
    except Exception as e:
        print(f"Error downloading image: {str(e)}")
        return None

    return None

@app.route('/preview/<path:url>')
def get_preview(url):
    print('hihi', url)
    try:
        decoded_url = unquote(url)
        print('hihi1', decoded_url)
        screenshot_path = get_screenshot(decoded_url)
        
        if screenshot_path and os.path.exists(screenshot_path):
            return send_file(screenshot_path, mimetype='image/png')
        else:
            # Return a 404 if no screenshot could be taken
            return '', 404
    except Exception as e:
        print(f"Error serving preview: {str(e)}")
        return str(e), 500

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    query = json.loads(data.get('query'))
    user_prefs = query['user_pref']

    asyncio.run(main(user_prefs, './logs', False, True))

    with open('sorted_listings.txt', 'r') as file:
        sorted_listings = file.read().splitlines()

    return jsonify({'sorted_listings': sorted_listings})


@app.route('/api/generate_query', methods=['POST'])
def generate_query():
    prompt = f"""
        Your task is to generate a personalized accommodation query based on the following criteria:
        1. Location/Vibe: Include a specific setting (e.g. mountains, beachfront, urban) and describe the atmosphere (e.g. cozy, modern, lively)
        2. Guests: Specify the number of people. Can include pets.
        3. Amenities: Highlight key features (e.g. fireplace, Wi-Fi, pool, washer, dryer)
        4. Budget: Provide budget for the stay.

        Be creative with your responses.

        Here's an example to follow:
        "I want a beachfront condo for four people. It must have a balcony with ocean views, free Wi-Fi, and a shared pool. 
        Bonus if it’s walking distance to restaurants and shops. My budget is $7000."
        """

    openai_client = OpenAI()
    response = openai_client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
    )

    query = response.choices[0].message.content.strip()
    return jsonify({'example_query': query})


def create_websurfer_subscription() -> Subscription:
    return Subscription(topic_id="web_surfer_topic")


async def main(user_prefs, logs_dir: str, hil_mode: bool, save_screenshots: bool) -> None:
    # Create the runtime.
    runtime = SingleThreadedAgentRuntime()

    # Create an appropriate client
    client = create_completion_client_from_env(model=MODEL_NAME)

    await ParsingAgent.register(runtime, "ParsingAgent", ParsingAgent)
    parsing_agent = AgentProxy(AgentId("ParsingAgent", "default"), runtime)

    await ListingFetchAgent.register(runtime, "ListingFetchAgent", ListingFetchAgent)
    listing_fetch = AgentProxy(AgentId("ListingFetchAgent", "default"), runtime)

    await BrowsingAgent.register(runtime, "BrowsingAgent", BrowsingAgent)
    browsing_agent = AgentProxy(AgentId("BrowsingAgent", "default"), runtime)

    await DescriptionAgent.register(runtime, "DescriptionAgent", DescriptionAgent)
    description_agent = AgentProxy(AgentId("DescriptionAgent", "default"), runtime)

    await ImageAnalysisAgent.register(runtime, "ImageAnalysisAgent", ImageAnalysisAgent)
    image_analysis = AgentProxy(AgentId("ImageAnalysisAgent", "default"), runtime)

    await RankingAgent.register(runtime, "RankingAgent", RankingAgent)
    ranking_agent = AgentProxy(AgentId("RankingAgent", "default"), runtime)

    await InitAgent.register(runtime, "InitAgent", InitAgent)
    init_agent = AgentProxy(AgentId("InitAgent", "default"), runtime)

    await LedgerOrchestrator.register(
        runtime, 
        "orchestrator", 
        lambda: LedgerOrchestrator(
            agents=[parsing_agent, listing_fetch, browsing_agent, description_agent, image_analysis, ranking_agent],
            model_client=client,
            max_stalls_before_replan=MAX_LISTING_COUNT,
        )
    )
    orchestrator = AgentProxy(AgentId("orchestrator", "default"), runtime)

    runtime.start()
    
    instructions = f"""
    Given the user preferences provided, use the agents at disposal to look in these listings for the best possible matches. Agents can access the chat history to see the outputs of other agents, so there is no need for the orchestrator to repeat details of agent outputs to other agents.

    Start with the Parsing Agent to parse the user's preferences. Then call the Listing Fetch Agent to get the listings' URLs. Then use the Browsing Agent to visit all the URLs outputted by the Listing Fetch Agent to provide summaries of each of the listings. After the summaries are provided, use the Description Agent to score the descriptions of each listing and the Image Analysis Agent to score the images of each listing. Finally, use the Ranking Agent to rank the listings based on the scores provided by both the Description Agent and the Image Analysis Agent.

    The Listing Fetch Agent should only be called once. When calling the browser agent you do not need to tell it which links to visit. The request is not satisfied until the Ranking Agent has been called. The request is satisfied immediately after the Ranking Agent outputs its results no matter what they are.
    
    User Preferences: {user_prefs}
    """.strip()

    await runtime.send_message(
        BroadcastMessage(
            content=UserMessage(
                content=instructions, source="User"
            )
        ),
        recipient=orchestrator.id,
        sender=init_agent.id,
    )
    await runtime.stop_when_idle()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run MagenticOne example with log directory.")
    parser.add_argument(
        "--logs_dir", 
        type=str, 
        default="./logs", 
        help="Directory to store log files and downloads (default: ./logs)"
    )
    parser.add_argument("--hil_mode", action="store_true", default=False, help="Run in human-in-the-loop mode")
    parser.add_argument(
        "--save_screenshots", action="store_true", default=False, help="Save additional browser screenshots to file"
    )
    parser.add_argument(
        "--start_page",
        type=str,
        default="https://www.airbnb.com/",
        help="The start page for the web surfer",
    )

    args = parser.parse_args()

    # Ensure the log directory exists
    if not os.path.exists(args.logs_dir):
        os.makedirs(args.logs_dir)

    logger = logging.getLogger(EVENT_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    log_handler = LogHandler(filename=os.path.join(args.logs_dir, "log.jsonl"))
    logger.handlers = [log_handler]

    # server code
    init_db()
    port = FLASK_PORT  # Specify the port you want to use
    print(f"Flask server running on http://localhost:{port}")
    app.run(debug=True, port=port)