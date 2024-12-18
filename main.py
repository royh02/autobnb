import asyncio
import logging
import os
import argparse
import json

from autogen_core import SingleThreadedAgentRuntime
from autogen_core.application.logging import EVENT_LOGGER_NAME
from autogen_core.base import AgentId, AgentProxy, Subscription
from autogen_magentic_one.agents.multimodal_web_surfer import MultimodalWebSurfer
from autogen_magentic_one.agents.orchestrator import LedgerOrchestrator
from autogen_magentic_one.agents.user_proxy import UserProxy
from autogen_magentic_one.messages import RequestReplyMessage
from autogen_magentic_one.utils import LogHandler, create_completion_client_from_env
from agents.init_agent import InitAgent
from agents.browsing_agent import BrowsingAgent
from agents.listing_fetch_agent import ListingFetchAgent
from agents.image_analysis_agent import ImageAnalysisAgent
from agents.ranking_agent import RankingAgent
from agents.description_agent import DescriptionAgent
from config import MODEL_NAME, MAX_LISTING_COUNT, FLASK_PORT

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

app = Flask(__name__)
cors = CORS(app)

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
    print(data.get('query'), type(data.get('query')))
    query = json.loads(data.get('query'))
    start_page, user_prefs = query['url'], query['user_pref']

    user_prefs['starting_url'] = start_page
    
    print('hihihi', query)

    file_path = 'user_request.txt'
    with open(file_path, 'w') as file:
        file.write(json.dumps(user_prefs))

    asyncio.run(main(start_page, './logs', False, True))

    with open('sorted_listings.txt', 'r') as file:
        sorted_listings = file.read().splitlines()

    return jsonify({'sorted_listings': sorted_listings})

def create_websurfer_subscription() -> Subscription:
    return Subscription(topic_id="web_surfer_topic")


async def main(start_page: str, logs_dir: str, hil_mode: bool, save_screenshots: bool) -> None:
    # Create the runtime.
    runtime = SingleThreadedAgentRuntime()

    # Create an appropriate client
    client = create_completion_client_from_env(model=MODEL_NAME)

    # Register agents.
    # await MultimodalWebSurfer.register(runtime, "WebSurfer", MultimodalWebSurfer)
    # web_surfer = AgentProxy(AgentId("WebSurfer", "default"), runtime)

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


    # to add additonal agents to the round robin orchestrator, add them to the list below after user_proxy
    await LedgerOrchestrator.register(
        runtime, 
        "orchestrator", 
        lambda: LedgerOrchestrator(
            agents=[init_agent, listing_fetch, browsing_agent, description_agent, image_analysis, ranking_agent],
            model_client=client,
            max_stalls_before_replan=MAX_LISTING_COUNT,
        )
    )

    runtime.start()

    # actual_surfer = await runtime.try_get_underlying_agent_instance(web_surfer.id, type=MultimodalWebSurfer)
    # await actual_surfer.init(
    #     model_client=client,
    #     downloads_folder=logs_dir,
    #     start_page=start_page,
    #     browser_channel="chromium",
    #     headless=True,
    #     debug_dir=logs_dir,
    #     to_save_screenshots=save_screenshots,
    # )

    await runtime.send_message(RequestReplyMessage(), init_agent.id)
    # await runtime.send_message(message, orchestrator.id)
    await runtime.stop_when_idle()

# def send_prompt():
#     user_prompt = request.json.get("prompt")
#     if not user_prompt:
#         return jsonify({"error": "Missing 'prompt' in request"}), 400

#     # Send the user prompt to the orchestrator
#     asyncio.run(_send_message_to_orchestrator(user_prompt))
#     return jsonify({"status": "Prompt sent to orchestrator successfully!"})

# async def _send_message_to_orchestrator(runtime, orchestrator, user_prompt: str):
#     """Send an initial message to the orchestrator."""
#     message = RequestReplyMessage(content=user_prompt, sender="User", receiver=orchestrator.id)
#     await runtime.send_message(message, orchestrator.id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run MagenticOne example with log directory.")
    parser.add_argument("--logs_dir", type=str, required=True, help="Directory to store log files and downloads")
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
    port = FLASK_PORT  # Specify the port you want to use
    print(f"Flask server running on http://localhost:{port}")
    app.run(debug=True, port=port)