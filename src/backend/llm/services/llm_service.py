"""
llm_service.py
==============

LLM Orchestration Service (Logging + Future PostgreSQL Ready)
"""

from typing import Any, Dict, List, AsyncGenerator
import time

from src.backend.core.config import settings
from src.backend.core.constants import DEFAULT_LLM_PROVIDER

import src.backend.llm.providers
from src.backend.llm.base.llm_providers import llm_provider_registry
from src.backend.guardrails.banlist_filter import BanListFilter

from src.backend.observability.logging.logger import get_logger


logger = get_logger(__name__)


class LLMService:
    """
    Main orchestration service untuk LLM interaction.
    """

    def __init__(self):
        self.banlist_filter = BanListFilter(
            banned_keywords=settings.BANNED_KEYWORDS
        )

        self.provider_name = DEFAULT_LLM_PROVIDER

        logger.info(
            "llm.service_initialized",
            extra={
                "event": "llm.service_initialized",
                "provider": self.provider_name,
                "default_model": settings.DEFAULT_LLM_MODEL,
            },
        )

    # =====================================================
    # INTERNAL PROVIDER FACTORY
    # =====================================================

    def _create_provider(self):
        """
        Create provider instance dari registry.
        """

        provider_cls = llm_provider_registry.get(self.provider_name)

        if not provider_cls:
            raise ValueError(f"Unknown LLM provider: {self.provider_name}")

        provider = provider_cls(
            model_name=settings.DEFAULT_LLM_MODEL,
            temperature=settings.DEFAULT_TEMPERATURE,
            max_tokens=settings.DEFAULT_MAX_TOKENS,
            timeout=settings.DEFAULT_TIMEOUT,
        )

        logger.info(
            "llm.provider_created",
            extra={
                "event": "llm.provider_created",
                "provider": self.provider_name,
                "model": settings.DEFAULT_LLM_MODEL,
            },
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
            logger.warning(
                "llm.guardrail_blocked",
                extra={
                    "event": "llm.guardrail_blocked",
                    "keyword": keyword,
                },
            )

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

        start_time = time.time()

        try:
            user_text = " ".join(
                msg["content"]
                for msg in messages
                if msg.get("role") == "user"
            )

            self._check_banlist(user_text)

            logger.info(
                "llm.generate_request",
                extra={
                    "event": "llm.generate_request",
                    "provider": self.provider_name,
                    "model": settings.DEFAULT_LLM_MODEL,
                    "message_count": len(messages),
                },
            )

            provider = self._create_provider()

            response = await provider.generate(
                messages=messages,
                **kwargs,
            )

            latency_ms = int((time.time() - start_time) * 1000)

            logger.info(
                "llm.generate_response",
                extra={
                    "event": "llm.generate_response",
                    "provider": self.provider_name,
                    "model": response.get("model"),
                    "latency_ms": latency_ms,
                    "usage": response.get("usage"),
                },
            )

            return response

        except Exception as e:
            logger.exception(
                "llm.generate_error",
                extra={
                    "event": "llm.generate_error",
                    "provider": self.provider_name,
                    "error": str(e),
                },
            )
            raise

    # =====================================================
    # STREAM RESPONSE (SSE)
    # =====================================================

    async def stream_generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Structured streaming response.
        """

        start_time = time.time()

        try:
            user_text = " ".join(
                msg["content"]
                for msg in messages
                if msg.get("role") == "user"
            )

            self._check_banlist(user_text)

            logger.info(
                "llm.stream_started",
                extra={
                    "event": "llm.stream_started",
                    "provider": self.provider_name,
                    "model": settings.DEFAULT_LLM_MODEL,
                    "message_count": len(messages),
                },
            )

            provider = self._create_provider()

            async for event in provider.stream_generate(
                messages=messages,
                **kwargs,
            ):
                yield event

            latency_ms = int((time.time() - start_time) * 1000)

            logger.info(
                "llm.stream_finished",
                extra={
                    "event": "llm.stream_finished",
                    "provider": self.provider_name,
                    "latency_ms": latency_ms,
                },
            )

        except Exception as e:
            logger.exception(
                "llm.stream_error",
                extra={
                    "event": "llm.stream_error",
                    "provider": self.provider_name,
                    "error": str(e),
                },
            )
            raise
