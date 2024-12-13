import json
from typing import Any, Dict, List, Optional

from autogen_core.base import AgentProxy, CancellationToken, MessageContext, TopicId
from autogen_core.components import default_subscription
from autogen_core.components.models import (
    AssistantMessage,
    ChatCompletionClient,
    LLMMessage,
    SystemMessage,
    UserMessage,
)

from autogen_magentic_one.messages import BroadcastMessage, OrchestrationEvent, ResetMessage
from autogen_magentic_one.agents.base_orchestrator import BaseOrchestrator
from autogen_magentic_one.agents.orchestrator_prompts import (
    ORCHESTRATOR_CLOSED_BOOK_PROMPT,
    ORCHESTRATOR_GET_FINAL_ANSWER,
    ORCHESTRATOR_LEDGER_PROMPT,
    ORCHESTRATOR_PLAN_PROMPT,
    ORCHESTRATOR_SYNTHESIZE_PROMPT,
    ORCHESTRATOR_SYSTEM_MESSAGE,
    ORCHESTRATOR_UPDATE_FACTS_PROMPT,
    ORCHESTRATOR_UPDATE_PLAN_PROMPT,
)


@default_subscription
class RoundRobinOrchestrator(BaseOrchestrator):
    """A simple orchestrator that selects agents in a round-robin fashion."""

    def __init__(
        self,
        agents: List[AgentProxy],
        description: str = "Round robin orchestrator",
        max_rounds: int = 20,
    ) -> None:
        super().__init__(agents=agents, description=description, max_rounds=max_rounds)

    async def _select_next_agent(self, message: LLMMessage) -> AgentProxy:
        self._current_index = (self._num_rounds) % len(self._agents)
        return self._agents[self._current_index]