"""
anthropic_provider.py
=====================

Native Anthropic provider menggunakan Anthropic SDK.
Tidak OpenAI-compatible — butuh SDK tersendiri.

Install: pip install anthropic
"""

from typing import Any, Dict, List

from backend.llm.base.llm_providers import BaseLLMProvider, llm_provider_registry
from backend.observability.logging.logger import get_logger

logger = get_logger(__name__)


class AnthropicProvider(BaseLLMProvider):

    def __init__(
        self,
        model_name: str,
        api_key: str,
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

        try:
            import anthropic
            self.client = anthropic.AsyncAnthropic(api_key=api_key)
        except ImportError:
            raise ImportError(
                "anthropic package not installed. Run: pip install anthropic"
            )

        logger.info(
            "provider.anthropic.init",
            extra={"event": "provider.anthropic.init", "model": model_name},
        )

    async def generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict[str, Any]:

        try:
            # Anthropic pisahkan system message dari messages
            system_prompt = None
            filtered_messages = []

            for msg in messages:
                if msg["role"] == "system":
                    system_prompt = msg["content"]
                else:
                    filtered_messages.append(msg)

            create_kwargs: Dict[str, Any] = {
                "model": self.model_name,
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "messages": filtered_messages,
            }

            if system_prompt:
                create_kwargs["system"] = system_prompt

            response = await self.client.messages.create(**create_kwargs)

            content = response.content[0].text if response.content else ""

            usage = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            }

            return self._build_response(
                content=content,
                raw=response,
                usage=usage,
                finish_reason=response.stop_reason,
            )

        except Exception as e:
            logger.exception("provider.anthropic.error", extra={"error": str(e)})
            raise RuntimeError(f"Anthropic generate error: {str(e)}")

    async def stream_generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ):
        full_content = ""
        token_count = 0

        try:
            system_prompt = None
            filtered_messages = []

            for msg in messages:
                if msg["role"] == "system":
                    system_prompt = msg["content"]
                else:
                    filtered_messages.append(msg)

            create_kwargs: Dict[str, Any] = {
                "model": self.model_name,
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "messages": filtered_messages,
            }

            if system_prompt:
                create_kwargs["system"] = system_prompt

            yield {
                "type": "start",
                "model": self.model_name,
                "provider": "anthropic",
            }

            async with self.client.messages.stream(**create_kwargs) as stream:
                async for text in stream.text_stream:
                    full_content += text
                    token_count += 1
                    yield {"type": "token", "content": text}

                final_message = await stream.get_final_message()
                usage = {
                    "prompt_tokens": final_message.usage.input_tokens,
                    "completion_tokens": final_message.usage.output_tokens,
                    "total_tokens": (
                        final_message.usage.input_tokens
                        + final_message.usage.output_tokens
                    ),
                }
                finish_reason = final_message.stop_reason

            yield {
                "type": "done",
                "full_content": full_content,
                "usage": usage,
                "finish_reason": finish_reason,
            }

        except Exception as e:
            logger.exception("provider.anthropic.stream_error", extra={"error": str(e)})
            raise RuntimeError(f"Anthropic streaming error: {str(e)}")


# Register
llm_provider_registry.register("anthropic", AnthropicProvider)