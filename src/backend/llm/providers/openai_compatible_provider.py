"""
openai_compatible_provider.py
==============================

Generic OpenAI-compatible provider.
Supports OpenRouter provider routing via extra_body.
"""

from typing import Any, Dict, List, Optional
import time

from openai import AsyncOpenAI

from backend.llm.base.llm_providers import BaseLLMProvider
from backend.observability.logging.logger import get_logger

logger = get_logger(__name__)


class OpenAICompatibleProvider(BaseLLMProvider):

    def __init__(
        self,
        model_name: str,
        api_key: str,
        base_url: str,
        provider_label: str = "openai-compatible",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        timeout: int = 60,
        # OpenRouter-specific provider routing
        provider_order: Optional[List[str]] = None,
        allow_fallbacks: bool = True,
        require_provider: bool = False,
    ):
        super().__init__(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
        )

        self.provider_label = provider_label
        self.provider_order = provider_order
        self.allow_fallbacks = allow_fallbacks
        self.require_provider = require_provider

        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
        )

        logger.info(
            f"provider.{provider_label}.init",
            extra={
                "event": f"provider.{provider_label}.init",
                "model": model_name,
                "base_url": base_url,
                "provider_order": provider_order,
            },
        )

    def _build_extra_body(self) -> Dict | None:
        """
        Build OpenRouter provider routing config.
        Only applies when provider_order is set.
        https://openrouter.ai/docs/provider-routing
        """
        if not self.provider_order:
            return None

        routing: Dict[str, Any] = {
            "order": self.provider_order,
            "allow_fallbacks": self.allow_fallbacks,
        }

        if self.require_provider:
            routing["require_parameters"] = True

        return {"provider": routing}

    async def generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict[str, Any]:

        start_time = time.time()

        try:
            create_kwargs: Dict[str, Any] = {
                "model": self.model_name,
                "messages": messages,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            }

            extra_body = self._build_extra_body()
            if extra_body:
                create_kwargs["extra_body"] = extra_body

            response = await self.client.chat.completions.create(**create_kwargs)

            content = response.choices[0].message.content if response.choices else ""

            usage = None
            if hasattr(response, "usage") and response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }

            finish_reason = response.choices[0].finish_reason if response.choices else None

            return self._build_response(
                content=content,
                raw=response,
                usage=usage,
                finish_reason=finish_reason,
            )

        except Exception as e:
            logger.exception(f"provider.{self.provider_label}.error", extra={"error": str(e)})
            raise RuntimeError(f"{self.provider_label} generate error: {str(e)}")

    async def stream_generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ):
        start_time = time.time()
        full_content = ""
        token_count = 0
        finish_reason = None

        try:
            create_kwargs: Dict[str, Any] = {
                "model": self.model_name,
                "messages": messages,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "stream": True,
            }

            extra_body = self._build_extra_body()
            if extra_body:
                create_kwargs["extra_body"] = extra_body

            stream = await self.client.chat.completions.create(**create_kwargs)

            yield {
                "type": "start",
                "model": self.model_name,
                "provider": self.provider_label,
            }

            async for chunk in stream:
                if not chunk.choices:
                    continue

                choice = chunk.choices[0]

                if choice.delta and choice.delta.content:
                    token = choice.delta.content
                    full_content += token
                    token_count += 1
                    yield {"type": "token", "content": token}

                if choice.finish_reason:
                    finish_reason = choice.finish_reason

            usage = {
                "prompt_tokens": 0,
                "completion_tokens": token_count,
                "total_tokens": token_count,
            }

            yield {
                "type": "done",
                "full_content": full_content,
                "usage": usage,
                "finish_reason": finish_reason,
            }

        except Exception as e:
            logger.exception(f"provider.{self.provider_label}.stream_error", extra={"error": str(e)})
            raise RuntimeError(f"{self.provider_label} streaming error: {str(e)}")