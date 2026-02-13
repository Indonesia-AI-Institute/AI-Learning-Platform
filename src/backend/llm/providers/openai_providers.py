"""
openai_provider.py
==================

Implementasi OpenAI LLM Provider.

Provider ini:
- Menggunakan OpenAI official python SDK
- Mengikuti interface BaseLLMProvider
- Support async generate
- Siap untuk future streaming (SSE)

NOTE:
Fokus saat ini:
✔ Backend API
✔ LLM API
❌ Database
❌ Tool calling complex orchestration
"""

from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

from llm.base.llm_providers import BaseLLMProvider, llm_provider_registry
from core.config import settings


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI LLM Provider Implementation.
    """

    def __init__(
        self,
        model_name: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        timeout: int = 60,
    ):
        """
        Initialize OpenAI Provider.
        """

        super().__init__(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
        )

        # Init OpenAI Async Client
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE,
            timeout=timeout,
        )

    # ======================================================
    # REQUIRED METHOD IMPLEMENTATION
    # ======================================================

    async def generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Generate non-stream response dari OpenAI.
        """

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
            )

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

            return self._build_response(
                content=content,
                raw=response,
                usage=usage,
                finish_reason=finish_reason,
            )

        except Exception as e:
            raise RuntimeError(f"OpenAI generate error: {str(e)}")

    # ======================================================
    # OPTIONAL STREAM METHOD (Future Ready)
    # ======================================================

    async def stream_generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ):
        """
        Streaming response untuk SSE.
        """

        try:
            stream = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                stream=True,
            )

            async for chunk in stream:
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta
                if not delta:
                    continue

                token = delta.content
                if token:
                    yield token

        except Exception as e:
            raise RuntimeError(f"OpenAI streaming error: {str(e)}")


# ======================================================
# REGISTER PROVIDER KE GLOBAL REGISTRY
# ======================================================

llm_provider_registry.register("openai", OpenAIProvider)
