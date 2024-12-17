import asyncio
import logging
import os
import argparse

from autogen_core import SingleThreadedAgentRuntime
from autogen_core.application.logging import EVENT_LOGGER_NAME
from autogen_core.base import AgentId, AgentProxy, Subscription
from autogen_magentic_one.agents.multimodal_web_surfer import MultimodalWebSurfer
from autogen_magentic_one.agents.orchestrator import LedgerOrchestrator
from autogen_magentic_one.agents.user_proxy import UserProxy
from autogen_magentic_one.messages import RequestReplyMessage
from autogen_magentic_one.utils import LogHandler, create_completion_client_from_env
from agents.init_agent import InitAgent
from agents.listing_fetch_agent import ListingFetchAgent
from agents.image_analysis_agent import ImageAnalysisAgent
from agents.ranking_agent import RankingAgent
from agents.description_agent import DescriptionAgent

from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio

app = Flask(__name__)
cors = CORS(app)

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query')
    start_page = data.get('start_page')
    
    print('hihihi', query)

    file_path = 'user_request.txt'
    with open(file_path, 'w') as file:
        file.write(query)

    asyncio.run(main(start_page, './logs', False, True))

    return jsonify({'message': 'Search request received', 'query': query})

def create_websurfer_subscription() -> Subscription:
    return Subscription(topic_id="web_surfer_topic")


async def main(start_page: str, logs_dir: str, hil_mode: bool, save_screenshots: bool) -> None:
    # Create the runtime.
    runtime = SingleThreadedAgentRuntime()

    # Create an appropriate client
    client = create_completion_client_from_env(model="gpt-4o-mini")

    # Register agents.
    await MultimodalWebSurfer.register(runtime, "WebSurfer", MultimodalWebSurfer)
    web_surfer = AgentProxy(AgentId("WebSurfer", "default"), runtime)

    await UserProxy.register(runtime, "UserProxy", UserProxy)
    user_proxy = AgentProxy(AgentId("UserProxy", "default"), runtime)

    await ListingFetchAgent.register(runtime, "ListingFetchAgent", ListingFetchAgent)
    listing_fetch = AgentProxy(AgentId("ListingFetchAgent", "default"), runtime)

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
            agents=[web_surfer, listing_fetch, init_agent, description_agent, image_analysis, ranking_agent],
            model_client=client
        )
    )

    runtime.start()

    actual_surfer = await runtime.try_get_underlying_agent_instance(web_surfer.id, type=MultimodalWebSurfer)
    await actual_surfer.init(
        model_client=client,
        downloads_folder=logs_dir,
        start_page=start_page,
        browser_channel="chromium",
        headless=True,
        debug_dir=logs_dir,
        to_save_screenshots=save_screenshots,
    )

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
    port = 5001  # Specify the port you want to use
    print(f"Flask server running on http://localhost:{port}")
    app.run(debug=True, port=port)