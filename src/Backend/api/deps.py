"""
deps.py
=======

Dependency Injection untuk FastAPI.

Fungsi:
- Menyediakan instance service (LLM Service, Chat Service, dll)
- Menghindari pembuatan object berulang di routes
- Mempermudah testing dan mocking

Current Scope:
✔ LLM Service
✔ Chat Service

Future:
- DB Session
- Auth Dependency
- Rate Limiter
"""

from functools import lru_cache

from services.chat_service import ChatService
from llm.service.llm_service import LLMService


# =========================================================
# LLM SERVICE DEPENDENCY
# =========================================================
@lru_cache()
def get_llm_service() -> LLMService:
    """
    Singleton LLM Service.

    Menggunakan lru_cache supaya:
    - Tidak recreate setiap request
    - Lebih hemat resource
    """

    return LLMService()


# =========================================================
# CHAT SERVICE DEPENDENCY
# =========================================================
@lru_cache()
def get_chat_service() -> ChatService:
    llm_service = get_llm_service()
    return ChatService(
        llm_service=llm_service
        )
