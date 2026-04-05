"""
provider_factory.py
===================
"""

from typing import List, Optional
from src.backend.core.config import settings
from src.backend.llm.base.llm_providers import BaseLLMProvider
from src.backend.observability.logging.logger import get_logger

logger = get_logger(__name__)


def _parse_provider_order(raw: str | None) -> Optional[List[str]]:
    """Parse comma-separated provider order string."""
    if not raw:
        return None
    return [p.strip() for p in raw.split(",") if p.strip()]


def create_llm_provider() -> BaseLLMProvider:

    provider_name = settings.DEFAULT_LLM_PROVIDER.lower()
    model_name = settings.DEFAULT_LLM_MODEL
    temperature = settings.DEFAULT_TEMPERATURE
    max_tokens = settings.DEFAULT_MAX_TOKENS
    timeout = settings.DEFAULT_TIMEOUT

    logger.info(
        "provider_factory.create",
        extra={
            "event": "provider_factory.create",
            "provider": provider_name,
            "model": model_name,
        },
    )

    # =====================================================
    # OPENAI
    # =====================================================
    if provider_name == "openai":
        from src.backend.llm.providers.openai_compatible_provider import OpenAICompatibleProvider

        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set.")

        return OpenAICompatibleProvider(
            model_name=model_name,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE,
            provider_label="openai",
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
        )

    # =====================================================
    # OPENROUTER
    # =====================================================
    elif provider_name == "openrouter":
        from src.backend.llm.providers.openai_compatible_provider import OpenAICompatibleProvider

        if not settings.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY is not set.")

        provider_order = _parse_provider_order(settings.OPENROUTER_PROVIDER_ORDER)

        if provider_order:
            logger.info(
                "provider_factory.openrouter_routing",
                extra={
                    "event": "provider_factory.openrouter_routing",
                    "provider_order": provider_order,
                    "allow_fallbacks": settings.OPENROUTER_ALLOW_FALLBACKS,
                },
            )

        return OpenAICompatibleProvider(
            model_name=model_name,
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_API_BASE,
            provider_label="openrouter",
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            provider_order=provider_order,
            allow_fallbacks=settings.OPENROUTER_ALLOW_FALLBACKS,
            require_provider=settings.OPENROUTER_REQUIRE_PROVIDER,
        )

    # =====================================================
    # GEMINI
    # =====================================================
    elif provider_name == "gemini":
        from src.backend.llm.providers.openai_compatible_provider import OpenAICompatibleProvider

        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set.")

        return OpenAICompatibleProvider(
            model_name=model_name,
            api_key=settings.GEMINI_API_KEY,
            base_url=settings.GEMINI_API_BASE,
            provider_label="gemini",
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
        )

    # =====================================================
    # ANTHROPIC
    # =====================================================
    elif provider_name == "anthropic":
        from src.backend.llm.providers.anthropic_provider import AnthropicProvider

        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is not set.")

        return AnthropicProvider(
            model_name=model_name,
            api_key=settings.ANTHROPIC_API_KEY,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
        )

    # =====================================================
    # CUSTOM
    # =====================================================
    elif provider_name == "custom":
        from src.backend.llm.providers.openai_compatible_provider import OpenAICompatibleProvider

        if not settings.CUSTOM_LLM_BASE_URL:
            raise ValueError("CUSTOM_LLM_BASE_URL is not set.")

        return OpenAICompatibleProvider(
            model_name=model_name,
            api_key=settings.CUSTOM_LLM_API_KEY or "custom",
            base_url=settings.CUSTOM_LLM_BASE_URL,
            provider_label="custom",
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
        )

    else:
        raise ValueError(
            f"Unknown provider: '{provider_name}'. "
            f"Valid: openai | openrouter | gemini | anthropic | custom"
        )