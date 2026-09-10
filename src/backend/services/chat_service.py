from typing import Any, Dict, List

from backend.agents.registry.agent_registry import AgentRegistry


class UnknownAgentError(Exception):
    """Raised when requested agent is not registered."""
    pass


class ChatService:
    """
    Main Chat Orchestration Layer.

    - Responsible for resolving agent
    - Delegating generate / stream
    - Does NOT contain business logic
    """

    def __init__(self, agent_registry: AgentRegistry):
        self.agent_registry = agent_registry

    def _get_agent(self, agent_type: str):
        agent = self.agent_registry.get_agent(agent_type)

        if not agent:
            raise UnknownAgentError(f"Unknown agent type: {agent_type}")

        return agent

    async def generate(
        self,
        agent_type: str,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Generate full response from agent.
        """

        agent = self._get_agent(agent_type)

        return await agent.generate(
            messages=messages,
            **kwargs,
        )

    async def stream_generate(
        self,
        agent_type: str,
        messages: list,
    ):
        agent = self._get_agent(agent_type)

        async for event in agent.stream_generate(messages=messages):
            yield event