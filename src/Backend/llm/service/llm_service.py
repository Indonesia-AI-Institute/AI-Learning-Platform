"""
llm_service.py
==============

Service layer untuk orchestrate LLM Provider usage.

Tanggung jawab:
- Select provider dari registry
- Apply guardrail filtering
- Handle streaming vs non-streaming
- Abstract provider logic dari chat service

Saat ini fokus:
✔ OpenAI only (via registry)
✔ SSE streaming support
✔ Banlist keyword guardrail
✔ Raw prompt passthrough

Future Ready:
- Multi provider routing (OpenRouter)
- Cost tracking
- Token analytics
- Conversation memory
"""

from typing import Any, Dict, List, AsyncGenerator

from core.config import settings
from core.constants import DEFAULT_LLM_PROVIDER

import llm.providers
from llm.base.llm_providers import llm_provider_registry
from guardrails.banlist_filter import BanListFilter


class LLMService:
    """
    Main orchestration service untuk LLM interaction.
    """

    def __init__(self):
        # Init guardrail filter
        self.banlist_filter = BanListFilter(
            banned_keywords=settings.BANNED_KEYWORDS
        )

        # Default provider
        self.provider_name = DEFAULT_LLM_PROVIDER

    # =====================================================
    # INTERNAL PROVIDER FACTORY
    # =====================================================

    def _create_provider(self):
        """
        Create provider instance dari registry.
        """

        provider_cls = llm_provider_registry.get(self.provider_name)

        provider = provider_cls(
            model_name=settings.DEFAULT_LLM_MODEL,
            temperature=settings.DEFAULT_TEMPERATURE,
            max_tokens=settings.DEFAULT_MAX_TOKENS,
            timeout=settings.DEFAULT_TIMEOUT,
        )

        return provider

    # =====================================================
    # GUARDRAIL CHECK
    # =====================================================

    def _check_banlist(self, text: str):
        """
        Raise error jika prompt kena banlist.
        """

        is_blocked, keyword = self.banlist_filter.check(text)

        if is_blocked:
            raise ValueError(f"Prompt contains banned keyword: {keyword}")

    # =====================================================
    # NON STREAM RESPONSE
    # =====================================================

    async def generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Generate full response (non streaming).
        """

        # Guardrail check → user prompt only
        user_text = " ".join(
            msg["content"] for msg in messages if msg.get("role") == "user"
        )

        self._check_banlist(user_text)

        provider = self._create_provider()

        response = await provider.generate(messages=messages, **kwargs)

        return response

    # =====================================================
    # STREAM RESPONSE (MAIN CHATBOT PATH - SSE)
    # =====================================================

    async def stream_generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """
        Streaming token generator untuk SSE.
        """

        # Guardrail check → user prompt only
        user_text = " ".join(
            msg["content"] for msg in messages if msg.get("role") == "user"
        )

        self._check_banlist(user_text)

        provider = self._create_provider()

        async for token in provider.stream_generate(messages=messages, **kwargs):
            yield token