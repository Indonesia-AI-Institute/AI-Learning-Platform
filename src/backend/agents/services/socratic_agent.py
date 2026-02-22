"""
socratic_tutor_agent.py
=======================

SocraticTutorAgent implements true multi-turn guided learning.
"""

from typing import Any, Dict, List, AsyncGenerator
import re
from .base_agent import BaseAgent


class SocraticTutorAgent(BaseAgent):
    """
    Multi-turn Socratic tutor agent.
    """

    def __init__(
        self,
        agent_config_path: str,
        llm_service: Any,
    ) -> None:
        super().__init__(agent_config_path, llm_service)

    # ======================================================
    # MAIN GENERATE (NON-STREAM)
    # ======================================================

    async def generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict[str, Any]:

        max_iterations = self.behavior_config.get("max_iterations", 3)

        assistant_messages = [
            msg for msg in messages if msg.get("role") == "assistant"
        ]

        if not assistant_messages:
            return await self._generate_guiding_question(messages, **kwargs)

        if len(assistant_messages) >= max_iterations:
            return await self._generate_final_explanation(messages, **kwargs)

        reflection_result = await self._run_reflection(messages)
        next_action = reflection_result.get("NEXT_ACTION")

        if next_action == "FINALIZE":
            return await self._generate_final_explanation(messages, **kwargs)

        if next_action == "HINT":
            return await self._generate_hint(messages, **kwargs)

        return await self._generate_guiding_question(messages, **kwargs)

    # ======================================================
    # STREAM VERSION (🔥 FIXED)
    # ======================================================

    async def stream_generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:

        max_iterations = self.behavior_config.get("max_iterations", 3)

        assistant_messages = [
            msg for msg in messages if msg.get("role") == "assistant"
        ]

        # =============================
        # DETERMINE STAGE (SAMA LOGIC generate())
        # =============================

        if not assistant_messages:
            stage = "QUESTION"

        elif len(assistant_messages) >= max_iterations:
            stage = "FINALIZE"

        else:
            reflection_result = await self._run_reflection(messages)
            stage = reflection_result.get("NEXT_ACTION", "QUESTION")

        # =============================
        # BUILD PROMPT SESUAI STAGE
        # =============================

        if stage == "FINALIZE":
            system_prompt = self.prompts.get("finalization_prompt", "")
        else:
            system_prompt = self.prompts.get("system_role", "")

        enriched = self._inject_system_prompt(messages, system_prompt)

        # =============================
        # STREAM KE LLM (TOKEN-BASED)
        # =============================

        async for chunk in self.llm_service.stream_generate(
            messages=enriched,
            **self.get_model_params(),
            **kwargs,
        ):
            yield chunk

    # ======================================================
    # STAGE METHODS (NON-STREAM)
    # ======================================================

    async def _generate_guiding_question(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict[str, Any]:

        system_prompt = self.prompts.get("system_role", "")
        enriched = self._inject_system_prompt(messages, system_prompt)

        return await self.llm_service.generate(
            messages=enriched,
            **self.get_model_params(),
            **kwargs,
        )

    async def _generate_hint(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict[str, Any]:

        system_prompt = self.prompts.get("system_role", "")
        enriched = self._inject_system_prompt(messages, system_prompt)

        return await self.llm_service.generate(
            messages=enriched,
            **self.get_model_params(),
            **kwargs,
        )

    async def _generate_final_explanation(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict[str, Any]:

        final_prompt = self.prompts.get("finalization_prompt", "")
        enriched = self._inject_system_prompt(messages, final_prompt)

        return await self.llm_service.generate(
            messages=enriched,
            **self.get_model_params(),
            **kwargs,
        )

    # ======================================================
    # REFLECTION (NON-STREAM, MEMANG HARUS)
    # ======================================================

    async def _run_reflection(
        self,
        messages: List[Dict[str, str]],
    ) -> Dict[str, str]:

        reflection_prompt = self.prompts.get("reflection_prompt", "")
        enriched = self._inject_system_prompt(messages, reflection_prompt)

        reflection_response = await self.llm_service.generate(
            messages=enriched,
            temperature=0.0,
            max_tokens=200,
        )

        content = self._extract_content(reflection_response)
        return self._parse_reflection(content)

    # ======================================================
    # UTILITIES
    # ======================================================

    def _inject_system_prompt(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
    ) -> List[Dict[str, str]]:

        if messages and messages[0].get("role") == "system":
            return messages

        return [{"role": "system", "content": system_prompt}] + messages

    def _extract_content(self, response: Dict[str, Any]) -> str:

        if "choices" in response:
            return response["choices"][0]["message"]["content"]

        return response.get("content", "")

    def _parse_reflection(self, text: str) -> Dict[str, str]:

        result = {
            "UNDERSTANDING_LEVEL": "LOW",
            "NEXT_ACTION": "QUESTION",
        }

        level_match = re.search(
            r"UNDERSTANDING_LEVEL:\s*(LOW|MEDIUM|HIGH)", text
        )
        action_match = re.search(
            r"NEXT_ACTION:\s*(QUESTION|HINT|FINALIZE)", text
        )

        if level_match:
            result["UNDERSTANDING_LEVEL"] = level_match.group(1)

        if action_match:
            result["NEXT_ACTION"] = action_match.group(1)

        return result