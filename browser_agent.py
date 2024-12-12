import asyncio
import logging
import os

from autogen_core.application import SingleThreadedAgentRuntime
from autogen_core.application.logging import EVENT_LOGGER_NAME
from autogen_core.base import AgentId, AgentProxy, Subscription
from autogen_magentic_one.agents.multimodal_web_surfer import MultimodalWebSurfer
from autogen_magentic_one.agents.orchestrator import RoundRobinOrchestrator
from autogen_magentic_one.agents.user_proxy import UserProxy
from autogen_magentic_one.messages import RequestReplyMessage
from autogen_magentic_one.utils import LogHandler, create_completion_client_from_env


def create_websurfer_subscription() -> Subscription:
    return Subscription(topic_id="web_surfer_topic")


async def main() -> None:
    # Create the runtime.
    runtime = SingleThreadedAgentRuntime()

    # Create an appropriate client
    client = create_completion_client_from_env(model="gpt-4o")

    # Register agents.
    await MultimodalWebSurfer.register(runtime, "WebSurfer", MultimodalWebSurfer)
    web_surfer = AgentProxy(AgentId("WebSurfer", "default"), runtime)

    await UserProxy.register(runtime, "UserProxy", UserProxy)
    user_proxy = AgentProxy(AgentId("UserProxy", "default"), runtime)

    # to add additonal agents to the round robin orchestrator, add them to the list below after user_proxy
    await RoundRobinOrchestrator.register(
        runtime, "orchestrator", lambda: RoundRobinOrchestrator([web_surfer, user_proxy])
    )

    runtime.start()

    actual_surfer = await runtime.try_get_underlying_agent_instance(web_surfer.id, type=MultimodalWebSurfer)
    await actual_surfer.init(
        model_client=client,
        downloads_folder=os.getcwd(),
        start_page="https://www.airbnb.com",
        browser_channel="chromium",
    )

    await runtime.send_message(RequestReplyMessage(), user_proxy.id)
    await runtime.stop_when_idle()


if __name__ == "__main__":
    logger = logging.getLogger(EVENT_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    log_handler = LogHandler()
    logger.handlers = [log_handler]
    asyncio.run(main())