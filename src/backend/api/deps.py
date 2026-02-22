"""
deps.py
=======

Dependency Injection untuk FastAPI.

Fungsi:
- Menyediakan instance LLM Service
- Menyediakan Agent Registry
- Menyediakan Chat Service (orchestration layer)
- Menghindari pembuatan object berulang
- Mempermudah testing dan mocking

Scope:
✔ LLM Service
✔ Agent Registry
✔ Chat Service

Future:
- DB Session
- Auth Dependency
- Rate Limiter
"""

from functools import lru_cache

from llm.services.llm_service import LLMService
from agents.registry.agent_registry import AgentRegistry
from services.chat_service import ChatService


# =========================================================
# LLM SERVICE (Singleton)
# =========================================================
@lru_cache()
def get_llm_service() -> LLMService:
    """
    Singleton LLM Service.
    """
    return LLMService()


# =========================================================
# AGENT REGISTRY (Singleton)
# =========================================================
@lru_cache()
def get_agent_registry() -> AgentRegistry:
    """
    Registry berisi semua agent (Direct, Socratic, dll).
    """
    llm_service = get_llm_service()
    return AgentRegistry(llm_service=llm_service)


# =========================================================
# CHAT SERVICE (Orchestration Layer)
# =========================================================
@lru_cache()
def get_chat_service() -> ChatService:
    """
    ChatService bertanggung jawab untuk:
    - Memilih agent
    - Menjalankan agent
    - Handle streaming / non-stream
    """
    registry = get_agent_registry()
    return ChatService(agent_registry=registry)
