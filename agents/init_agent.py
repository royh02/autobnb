from typing import Tuple
from autogen_core.base import CancellationToken
from autogen_core.components import default_subscription
from autogen_magentic_one.messages import (
    BroadcastMessage,
    RequestReplyMessage,
    ResetMessage,
    UserContent,
)
from autogen_magentic_one.agents.base_worker import BaseWorker


@default_subscription
class InitAgent(BaseWorker):
    """An agent that processes user input and fetches Airbnb listings."""

    DEFAULT_DESCRIPTION = """You are a proxy agent that receives instructions and passes it to the orchestrator to use to start the process."""

    def __init__(
        self,
        description: str = DEFAULT_DESCRIPTION,
        client=None,  # Optional client for extended functionality
    ) -> None:
        super().__init__(description)
        self._client = client

    async def _generate_reply(self, cancellation_token: CancellationToken) -> Tuple[bool, UserContent]:
        """
        Output the user input as a response.

        Args:
            cancellation_token (CancellationToken): Token to check for cancellation

        Returns:
            Tuple[bool, UserContent]: Indicates if the process should halt and the generated content.
        """
        try:
            # Get the latest user prompt from chat history

            with open('user_request.txt', 'r') as file:
                user_input = file.read()
            
            response = f"""
            Given the user preferences provided, use the agents at disposal to look in these listings for the best possible matches. Agents can access the chat history to see the outputs of other agents, so there is no need for the orchestrator to repeat details of agent outputs to other agents.
            
            Start with the Parsing Agent to parse the user's preferences. Then call the Listing Fetch Agent to get the listings' URLs. Then use the Browsing Agent to visit all the URLs outputted by the Listing Fetch Agent to provide summaries of each of the listings. After the summaries are provided, use the Description Agent to score the descriptions of each listing and the Image Analysis Agent to score the images of each listing. Finally, use the Ranking Agent to rank the listings based on the scores provided by both the Description Agent and the Image Analysis Agent.

            The Listing Fetch Agent should only be called once. When calling the browser agent you do not need to tell it which links to visit. The request is not satisfied until the Ranking Agent has been called.

            ### User Preferences: {user_input}
            """
            
            return False, response

        except Exception as e:
            return False, f"Error fetching listings: {str(e)}"
        