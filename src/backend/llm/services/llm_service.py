"""
LLM orchestration service. Provider dipilih berdasarkan ENV config via provider_factory.
"""

from typing import Any, Dict, List, AsyncGenerator
import time

from backend.core.config import settings
from backend.llm.providers.provider_factory import create_llm_provider
from backend.guardrails.banlist_filter import BanListFilter
from backend.observability.logging.logger import get_logger

logger = get_logger(__name__)


class LLMService:
    """
    Main orchestration service untuk LLM interaction.
    Provider di-create fresh setiap request (stateless).
    """

    def __init__(self):
        self.banlist_filter = BanListFilter(
            banned_keywords=settings.BANNED_KEYWORDS
        )

        logger.info(
            "llm.service_initialized",
            extra={
                "event": "llm.service_initialized",
                "provider": settings.DEFAULT_LLM_PROVIDER,
                "model": settings.DEFAULT_LLM_MODEL,
            },
        )

    def _create_provider(self):
        """
        Create provider instance dari factory berdasarkan ENV config.
        """
        return create_llm_provider()

    def _check_banlist(self, text: str):
        is_blocked, keyword = self.banlist_filter.check(text)
        if is_blocked:
            logger.warning(
                "llm.guardrail_blocked",
                extra={"event": "llm.guardrail_blocked", "keyword": keyword},
            )
            raise ValueError(f"Prompt contains banned keyword: {keyword}")

    async def generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict[str, Any]:

        start_time = time.time()

        try:
            user_text = " ".join(
                msg["content"] for msg in messages if msg.get("role") == "user"
            )
            self._check_banlist(user_text)

            provider = self._create_provider()
            response = await provider.generate(messages=messages, **kwargs)

            latency_ms = int((time.time() - start_time) * 1000)

            logger.info(
                "llm.generate_response",
                extra={
                    "event": "llm.generate_response",
                    "provider": settings.DEFAULT_LLM_PROVIDER,
                    "model": response.get("model", settings.DEFAULT_LLM_MODEL),
                    "latency_ms": latency_ms,
                },
            )

            return response

        except Exception as e:
            logger.exception(
                "llm.generate_error",
                extra={"event": "llm.generate_error", "error": str(e)},
            )
            raise

    async def stream_generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> AsyncGenerator[Dict[str, Any], None]:

        start_time = time.time()

        try:
            user_text = " ".join(
                msg["content"] for msg in messages if msg.get("role") == "user"
            )
            self._check_banlist(user_text)

            provider = self._create_provider()

            async for event in provider.stream_generate(messages=messages, **kwargs):
                yield event

            latency_ms = int((time.time() - start_time) * 1000)

            logger.info(
                "llm.stream_finished",
                extra={
                    "event": "llm.stream_finished",
                    "provider": settings.DEFAULT_LLM_PROVIDER,
                    "latency_ms": latency_ms,
                },
            )

        except Exception as e:
            logger.exception(
                "llm.stream_error",
                extra={"event": "llm.stream_error", "error": str(e)},
            )
            raise