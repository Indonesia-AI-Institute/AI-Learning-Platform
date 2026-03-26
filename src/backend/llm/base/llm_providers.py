"""
llm_providers.py
================

Base abstraction untuk semua LLM provider.

Tujuan:
- Standardisasi interface antar provider (OpenAI, OpenRouter, dll)
- Memudahkan model switching di masa depan
- Memisahkan logic LLM dari business logic service

Saat ini digunakan untuk:
✔ OpenAI Provider
✔ Streaming (SSE)
✔ Non-stream response

Future Ready:
- Multi provider routing
- Model cost tracking
- Tool calling orchestration
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, AsyncGenerator


# =========================================================
# BASE PROVIDER ABSTRACT CLASS
# =========================================================

class BaseLLMProvider(ABC):
    """
    Base class untuk semua LLM Provider.
    Semua provider HARUS implement generate().
    Streaming optional tapi strongly recommended (karena kita pakai SSE).
    """

    def __init__(
        self,
        model_name: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        timeout: int = 60,
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

    # =====================================================
    # REQUIRED METHOD
    # =====================================================

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Generate full response (non streaming).

        Returns:
            Dict berisi:
            - content
            - usage
            - finish_reason
            - raw response
        """
        pass

    # =====================================================
    # OPTIONAL STREAM METHOD
    # =====================================================

    async def stream_generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """
        Streaming token generator.
        Default -> Not implemented.
        Provider boleh override kalau support streaming.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support streaming."
        )

    # =====================================================
    # HELPER
    # =====================================================

    def _build_response(
        self,
        content: str,
        raw: Any,
        usage: Optional[Dict[str, Any]] = None,
        finish_reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Standard response formatter.
        """

        return {
            "content": content,
            "usage": usage,
            "finish_reason": finish_reason,
            "raw": raw,
        }


# =========================================================
# PROVIDER REGISTRY
# =========================================================

class LLMProviderRegistry:
    """
    Registry global untuk semua provider.

    Contoh:
    registry.register("openai", OpenAIProvider)
    provider = registry.get("openai")
    """

    def __init__(self):
        self._providers: Dict[str, type[BaseLLMProvider]] = {}

    def register(self, name: str, provider_cls: type[BaseLLMProvider]):
        """
        Register provider class.
        """
        self._providers[name.lower()] = provider_cls

    def get(self, name: str) -> type[BaseLLMProvider]:
        """
        Ambil provider class dari registry.
        """
        provider = self._providers.get(name.lower())

        if not provider:
            raise ValueError(f"Provider '{name}' not registered.")

        return provider

    def list_providers(self) -> List[str]:
        """
        List semua provider yang tersedia.
        """
        return list(self._providers.keys())


# =========================================================
# GLOBAL REGISTRY INSTANCE
# =========================================================

llm_provider_registry = LLMProviderRegistry()
