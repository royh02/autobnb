import asyncio
import logging
import os
import argparse
import json
import hashlib

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

from flask import Flask, request, jsonify, send_file, Response, send_from_directory
from flask_cors import CORS
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import sqlite3
from flask import g
import uuid

app = Flask(__name__, static_folder="static/build", static_url_path="")
cors = CORS(app)

@app.route("/")
def serve():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    if path and (app.static_folder / path).exists():
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")

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

@app.route('/preview/<path:url>')
def get_preview(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-accelerated-2d-canvas",
                    "--no-zygote",
                    "--single-process",  # Required for some Docker environments
                    "--disable-web-security",
                ],
            )
            context = browser.new_context()
            page = context.new_page()

            page.goto(url, timeout=20000)
            content = page.content()
            soup = BeautifulSoup(content, 'html.parser')

            image_urls = []

            # Extract images from <picture> tags
            for picture in soup.find_all('picture', recursive=True):
                if len(image_urls) < 5:
                    img = picture.find('img')
                    if img and (src := img.get('src')) and not src.endswith(('.gif', '.svg')):
                        image_urls.append(src)

            # Extract preloaded images
            if len(image_urls) < 5:
                for link in soup.find_all('link', {'rel': 'preload', 'as': 'image'}):
                    if (href := link.get('href')) and not href.endswith(('.gif', '.svg')):
                        image_urls.append(href)
                        if len(image_urls) >= 5:
                            break

            # Extract meta images
            if len(image_urls) < 5:
                meta_images = soup.find_all('meta', {'property': 'og:image'}) or soup.find_all('meta', {'itemprop': 'image'})
                for meta in meta_images:
                    if (content := meta.get('content')) and not content.endswith(('.gif', '.svg')):
                        image_urls.append(content)
                        if len(image_urls) >= 5:
                            break

            browser.close()
            return jsonify(image_urls)

    except Exception as e:
        print(f"Error fetching preview: {str(e)}")
        return jsonify([]), 500

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    query = json.loads(data.get('query'))

    user_prefs = query['user_pref']
    if user_prefs['key']:
        os.environ["OPENAI_API_KEY"] = user_prefs['key']
    del user_prefs['key']

    result_id = str(uuid.uuid4())
    asyncio.run(main(user_prefs, result_id, './logs', False, True))

    db = get_db()
    cur = db.execute("SELECT id, data FROM my_table WHERE id = ?", (result_id,))
    row = cur.fetchone()
    sorted_listings = json.loads(row[1])
    print(json.dumps(sorted_listings, indent=2))

    return jsonify({'sorted_listings': sorted_listings})

@app.route('/api/generate_query', methods=['POST'])
def generate_query():
    data = request.json
    query = json.loads(data.get('query'))
    user_prefs = query['user_pref']
    if user_prefs['key']:
        os.environ["OPENAI_API_KEY"] = user_prefs['key']

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

async def main(user_prefs, result_id, logs_dir: str, hil_mode: bool, save_screenshots: bool) -> None:
    runtime = SingleThreadedAgentRuntime()

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
    Given the user preferences provided, use the agents at your disposal to look in these listings for the best possible matches. Agents can access the chat history to see the outputs of other agents, so there is no need for the orchestrator to repeat details of agent outputs to other agents.

    Call each of the following agents exactly once in this order:
    1. Parsing Agent
    2. Listing Fetch Agent
    3. Browsing Agent
    4. Description Agent
    5. Image Analysis Agent
    6. Ranking Agent

    When calling the browser agent you do not need to tell it which links to visit. The request is not satisfied until the Ranking Agent has been called. The request is satisfied immediately after the Ranking Agent is called.

    User Preferences: {user_prefs}

    Final Result ID: {result_id}
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

    if not os.path.exists(args.logs_dir):
        os.makedirs(args.logs_dir)

    logger = logging.getLogger(EVENT_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    log_handler = LogHandler(filename=os.path.join(args.logs_dir, "log.jsonl"))
    logger.handlers = [log_handler]

    init_db()
    port = FLASK_PORT
    print(f"Flask server running on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)