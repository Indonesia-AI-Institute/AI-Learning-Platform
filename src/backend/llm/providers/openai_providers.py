"""
openai_provider.py
==================

OpenAI Provider with Production Logging.
"""

import time
from typing import Any, Dict, List

from backend.core.config import settings
from backend.llm.base.llm_providers import BaseLLMProvider, llm_provider_registry
from backend.observability.logging.logger import get_logger
from openai import AsyncOpenAI

logger = get_logger(__name__)


class OpenAIProvider(BaseLLMProvider):

    def __init__(
        self,
        model_name: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        timeout: int = 60,
    ):

        super().__init__(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
        )

        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE,
            timeout=timeout,
        )

        logger.info(
            "provider.openai.init",
            extra={
                "event": "provider.openai.init",
                "model": model_name,
                "timeout": timeout,
                "has_api_key": bool(settings.OPENAI_API_KEY),
            },
        )

    async def generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict[str, Any]:

        start_time = time.time()

        try:
            logger.info(
                "provider.openai.request",
                extra={
                    "event": "provider.openai.request",
                    "model": self.model_name,
                    "message_count": len(messages),
                    "temperature": kwargs.get("temperature", self.temperature),
                },
            )

            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
            )

            latency_ms = int((time.time() - start_time) * 1000)

            content = response.choices[0].message.content if response.choices else ""

            usage = None
            if hasattr(response, "usage") and response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }

            finish_reason = None
            if response.choices:
                finish_reason = response.choices[0].finish_reason

            logger.info(
                "provider.openai.response",
                extra={
                    "event": "provider.openai.response",
                    "model": self.model_name,
                    "latency_ms": latency_ms,
                    "finish_reason": finish_reason,
                    "usage": usage,
                },
            )

            return self._build_response(
                content=content,
                raw=response,
                usage=usage,
                finish_reason=finish_reason,
            )

        except Exception as e:
            logger.exception(
                "provider.openai.error",
                extra={
                    "event": "provider.openai.error",
                    "model": self.model_name,
                    "error": str(e),
                },
            )
            raise RuntimeError(f"OpenAI generate error: {str(e)}")

    async def stream_generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ):
        """
        Streaming dengan structured event.
        """

        start_time = time.time()
        full_content = ""
        token_count = 0
        finish_reason = None

        try:
            logger.info(
                "provider.openai.stream_start",
                extra={
                    "event": "provider.openai.stream_start",
                    "model": self.model_name,
                    "message_count": len(messages),
                },
            )

            stream = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                stream=True,
            )
            yield {
                "type": "start",
                "model": self.model_name,
                "provider": "openai",
            }

            async for chunk in stream:

                if not chunk.choices:
                    continue

                choice = chunk.choices[0]

                if choice.delta and choice.delta.content:
                    token = choice.delta.content
                    full_content += token
                    token_count += 1

                    yield {
                        "type": "token",
                        "content": token,
                    }

                if choice.finish_reason:
                    finish_reason = choice.finish_reason

            latency_ms = int((time.time() - start_time) * 1000)

            logger.info(
                "provider.openai.stream_end",
                extra={
                    "event": "provider.openai.stream_end",
                    "model": self.model_name,
                    "latency_ms": latency_ms,
                    "stream_token_count": token_count,
                    "finish_reason": finish_reason,
                },
            )
            usage = {
                "prompt_tokens": 0,
                "completion_tokens": token_count,
                "total_tokens": token_count,
            }
            yield {
                "type": "done",
                "full_content": full_content,
                "usage": usage,  # streaming OpenAI v1 tidak kirim usage
                "finish_reason": finish_reason,
            }

        except Exception as e:
            logger.exception(
                "provider.openai.stream_error",
                extra={
                    "event": "provider.openai.stream_error",
                    "model": self.model_name,
                    "error": str(e),
                },
            )
            raise RuntimeError(f"OpenAI streaming error: {str(e)}")


llm_provider_registry.register("openai", OpenAIProvider)
