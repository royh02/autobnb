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
            The web surfer agent will be started on a Airbnb page with potential listings.
            Given the user input, use the agents at disposal to achieve the user input's specified goal.

            ### User input: {user_input}
            """
            
            return False, response

        except Exception as e:
            return False, f"Error fetching listings: {str(e)}"
        