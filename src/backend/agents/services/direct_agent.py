"""
DirectTutorAgent implements single-pass direct explanation behavior.
"""

from typing import Any, Dict, List, AsyncGenerator
from .base_agent import BaseAgent


class DirectTutorAgent(BaseAgent):
    """
    Single-pass direct tutor agent.
    """

    def __init__(
        self,
        agent_config_path: str,
        llm_service: Any,
    ) -> None:
        super().__init__(agent_config_path, llm_service)

    async def generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict[str, Any]:

        system_prompt = self.get_system_prompt()
        model_params = self.get_model_params()

        enriched_messages = self._inject_system_prompt(
            messages,
            system_prompt,
        )

        return await self.llm_service.generate(
            messages=enriched_messages,
            **model_params,
            **kwargs,
        )

    async def stream_generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:

        system_prompt = self.get_system_prompt()
        model_params = self.get_model_params()

        enriched_messages = self._inject_system_prompt(
            messages,
            system_prompt,
        )

        async for token in self.llm_service.stream_generate(
            messages=enriched_messages,
            **model_params,
            **kwargs,
        ):
            yield token

    def _inject_system_prompt(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
    ) -> List[Dict[str, str]]:

        if messages and messages[0].get("role") == "system":
            return messages

        return [{"role": "system", "content": system_prompt}] + messages
