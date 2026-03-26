"""
deps.py
=======

Dependency Injection Layer
"""

from functools import lru_cache

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.llm.services.llm_service import LLMService
from src.backend.agents.registry.agent_registry import AgentRegistry
from src.backend.services.chat_service import ChatService

from src.backend.db.session import get_db
from src.backend.models.user import User, UserRole
from src.backend.repositories.user_repository import UserRepository
from src.backend.auth.security import decode_access_token

# =========================
# SECURITY SCHEME
# =========================
security = HTTPBearer(auto_error=False)  # auto_error=False supaya tidak langsung 403 jika tidak ada Bearer


# =========================================================
# LLM SERVICE (Singleton)
# =========================================================

@lru_cache()
def get_llm_service() -> LLMService:
    return LLMService()


@lru_cache()
def get_agent_registry() -> AgentRegistry:
    llm_service = get_llm_service()
    return AgentRegistry(llm_service=llm_service)


@lru_cache()
def get_chat_service() -> ChatService:
    registry = get_agent_registry()
    return ChatService(agent_registry=registry)


# =========================================================
# AUTH DEPENDENCY
# =========================================================

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Resolve token dari dua sumber:
    1. httpOnly cookie (frontend web)
    2. Authorization: Bearer header (Swagger / mobile / API client)

    Cookie diprioritaskan, Bearer sebagai fallback.
    """

    token: str | None = None

    # 1️⃣ Coba dari cookie dulu
    token = request.cookies.get("access_token")

    # 2️⃣ Fallback ke Bearer header
    if not token and credentials:
        token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id: str | None = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user_repo = UserRepository(db)
    user = await user_repo.get(user_id)

    if not user or user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user


# =========================================================
# ROLE DEPENDENCIES
# =========================================================

async def require_teacher(
    current_user: User = Depends(get_current_user),
) -> User:

    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires teacher role",
        )

    return current_user


async def require_student(
    current_user: User = Depends(get_current_user),
) -> User:

    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires student role",
        )

    return current_user