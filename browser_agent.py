import asyncio
import logging
import os
import argparse

from autogen_core.application import SingleThreadedAgentRuntime
from autogen_core.application.logging import EVENT_LOGGER_NAME
from autogen_core.base import AgentId, AgentProxy, Subscription
from autogen_magentic_one.agents.multimodal_web_surfer import MultimodalWebSurfer
from autogen_magentic_one.agents.orchestrator import RoundRobinOrchestrator, LedgerOrchestrator
from autogen_magentic_one.agents.user_proxy import UserProxy
from autogen_magentic_one.messages import RequestReplyMessage
from autogen_magentic_one.utils import LogHandler, create_completion_client_from_env
from agents.listing_fetch_agent import ListingFetchAgent


def create_websurfer_subscription() -> Subscription:
    return Subscription(topic_id="web_surfer_topic")


async def main(logs_dir: str, hil_mode: bool, save_screenshots: bool) -> None:
    # Create the runtime.
    runtime = SingleThreadedAgentRuntime()

    # Create an appropriate client
    client = create_completion_client_from_env(model="gpt-4o")

    # Register agents.
    await MultimodalWebSurfer.register(runtime, "WebSurfer", MultimodalWebSurfer)
    web_surfer = AgentProxy(AgentId("WebSurfer", "default"), runtime)

    # await UserProxy.register(runtime, "UserProxy", UserProxy)
    # user_proxy = AgentProxy(AgentId("UserProxy", "default"), runtime)

    await ListingFetchAgent.register(runtime, "ListingFetchAgent", ListingFetchAgent)
    listing_fetch = AgentProxy(AgentId("ListingFetchAgent", "default"), runtime)

    # to add additonal agents to the round robin orchestrator, add them to the list below after user_proxy
    await LedgerOrchestrator.register(
        runtime, 
        "orchestrator", 
        lambda: LedgerOrchestrator(
            agents=[web_surfer, listing_fetch],
            model_client=client
        )
    )

    runtime.start()

    actual_surfer = await runtime.try_get_underlying_agent_instance(web_surfer.id, type=MultimodalWebSurfer)
    await actual_surfer.init(
        model_client=client,
        downloads_folder=logs_dir,
        start_page="https://www.airbnb.com/?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&search_mode=flex_destinations_search&flexible_trip_lengths%5B%5D=one_week&location_search=MIN_MAP_BOUNDS&monthly_start_date=2025-01-01&monthly_length=3&monthly_end_date=2025-04-01&category_tag=Tag%3A5348&price_filter_input_type=2&channel=EXPLORE&date_picker_type=calendar&adults=2&search_type=filter_change&price_filter_num_nights=5&min_bedrooms=2&min_beds=1&amenities%5B%5D=4&amenities%5B%5D=8",
        browser_channel="chromium",
        headless=True,
        debug_dir=logs_dir,
        to_save_screenshots=save_screenshots,
    )

    await runtime.send_message(RequestReplyMessage(), listing_fetch.id)
    await runtime.stop_when_idle()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run MagenticOne example with log directory.")
    parser.add_argument("--logs_dir", type=str, required=True, help="Directory to store log files and downloads")
    parser.add_argument("--hil_mode", action="store_true", default=False, help="Run in human-in-the-loop mode")
    parser.add_argument(
        "--save_screenshots", action="store_true", default=False, help="Save additional browser screenshots to file"
    )

    args = parser.parse_args()

    # Ensure the log directory exists
    if not os.path.exists(args.logs_dir):
        os.makedirs(args.logs_dir)

    logger = logging.getLogger(EVENT_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    log_handler = LogHandler(filename=os.path.join(args.logs_dir, "log.jsonl"))
    logger.handlers = [log_handler]
    asyncio.run(main(args.logs_dir, args.hil_mode, args.save_screenshots))