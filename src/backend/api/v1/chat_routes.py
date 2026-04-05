"""
chat_routes.py
==============
Chat API Routes (Split Agent Architecture).
"""

from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.utils.role_guard import RoleGuard
from src.backend.api.deps import (
    get_db,
    get_current_user,
    get_chat_service,
)
from src.backend.services.prompt_classification_service import PromptClassificationService
from src.backend.llm.services.llm_service import LLMService
from src.backend.api.deps import get_llm_service
from src.backend.services.session_service import SessionService
from src.backend.services.chat_history_service import ChatHistoryService
from src.backend.services.chat_service import ChatService
from src.backend.services.conversation_service import ConversationService

from src.backend.models.user import User, UserRole

from src.backend.schemas.chat.chat_request import ChatRequest
from src.backend.schemas.chat.chat_response import ChatResponse
from src.backend.schemas.chat.chat_session_response import ChatSessionResponse
from src.backend.schemas.chat.chat_session_create_request import ChatSessionCreateRequest
from src.backend.schemas.chat.chat_history_response import ChatHistoryResponse, ChatMessageItem

from src.backend.utils.streaming_utils import sse_stream_wrapper


router = APIRouter(prefix="/chat", tags=["Chat"])


# =========================================================
# DEPENDENCY BUILDER
# =========================================================

def get_conversation_service(
    db: AsyncSession = Depends(get_db),
    chat_service: ChatService = Depends(get_chat_service),
) -> ConversationService:
 
    session_service = SessionService(db)
    history_service = ChatHistoryService(db)
    classification_service = PromptClassificationService(db)
    llm_service = LLMService()
 
    return ConversationService(
        session_service=session_service,
        history_service=history_service,
        chat_service=chat_service,
        classification_service=classification_service,
        llm_service=llm_service,
    )


# =========================================================
# DIRECT AGENT (STATELESS)
# =========================================================

@router.post("/direct/stream")
async def stream_direct_chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
):

    async def event_stream():

        messages = []

        if request.system_prompt:
            messages.append({
                "role": "system",
                "content": request.system_prompt,
            })

        messages.extend([msg.model_dump() for msg in request.messages])

        async for event in chat_service.stream_generate(
            agent_type="direct_tutor",
            messages=messages,
        ):
            if event["type"] == "token":
                yield event["content"]

    return StreamingResponse(
        sse_stream_wrapper(event_stream()),
        media_type="text/event-stream",
    )


@router.post("/direct/generate", response_model=ChatResponse)
async def generate_direct_chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
):

    messages = []

    if request.system_prompt:
        messages.append({
            "role": "system",
            "content": request.system_prompt,
        })

    messages.extend([msg.model_dump() for msg in request.messages])

    response = await chat_service.generate(
        agent_type="direct_tutor",
        messages=messages,
    )

    return ChatResponse(
        response_text=response["content"]
    )


# =========================================================
# CREATE SESSION
# =========================================================

@router.post("/sessions/task/{task_id}", response_model=ChatSessionResponse)
async def create_session(
    task_id: UUID,
    request: ChatSessionCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleGuard([UserRole.STUDENT])),
):
    service = SessionService(db)

    try:
        session = await service.create_session(
            current_user=current_user,
            task_id=task_id,
            title=request.title,
        )
        return session

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# =========================================================
# GET MY SESSIONS (Student)
# =========================================================

@router.get("/sessions/my", response_model=List[ChatSessionResponse])
async def get_my_sessions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleGuard([UserRole.STUDENT])),
):
    service = SessionService(db)

    try:
        sessions = await service.get_my_sessions(
            current_user=current_user,
            skip=skip,
            limit=limit,
        )
        return sessions

    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# =========================================================
# GET SESSIONS BY TASK (Student)
# Digunakan di /tasks/{id} untuk tampilkan list session
# dan tombol resume
# =========================================================

@router.get("/sessions/task/{task_id}", response_model=List[ChatSessionResponse])
async def get_sessions_by_task(
    task_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleGuard([UserRole.STUDENT])),
):
    service = SessionService(db)

    try:
        sessions = await service.get_sessions_by_task(
            current_user=current_user,
            task_id=task_id,
            skip=skip,
            limit=limit,
        )
        return sessions

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# =========================================================
# SESSION CHAT (STATEFUL)
# =========================================================

@router.post("/sessions/{session_id}/stream")
async def stream_session_chat(
    session_id: UUID,
    request: ChatRequest,
    current_user: User = Depends(RoleGuard([UserRole.STUDENT])),
    conversation_service: ConversationService = Depends(get_conversation_service),
):

    if not request.messages:
        raise HTTPException(status_code=400, detail="No message provided")

    user_message = request.messages[-1].content

    async def event_stream():

        async for token in conversation_service.stream_message(
            current_user=current_user,
            session_id=session_id,
            agent_type="direct_tutor",
            content=user_message,
            system_prompt=request.system_prompt,
        ):
            yield token

    return StreamingResponse(
        sse_stream_wrapper(event_stream()),
        media_type="text/event-stream",
    )


# =========================================================
# END SESSION
# =========================================================

@router.post("/sessions/{session_id}/end", response_model=ChatSessionResponse)
async def end_chat_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleGuard([UserRole.STUDENT])),
):
    session_service = SessionService(db)

    try:
        session = await session_service.end_session(
            current_user=current_user,
            session_id=session_id,
        )
        return session

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# =========================================================
# RESUME SESSION
# =========================================================

@router.post("/sessions/{session_id}/resume", response_model=ChatSessionResponse)
async def resume_chat_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleGuard([UserRole.STUDENT])),
):
    session_service = SessionService(db)

    try:
        session = await session_service.resume_session(
            current_user=current_user,
            session_id=session_id,
        )
        return session

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# =========================================================
# GET CHAT HISTORY
# =========================================================

@router.get("/sessions/{session_id}/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleGuard([UserRole.STUDENT])),
):
    session_service = SessionService(db)
    history_service = ChatHistoryService(db)

    try:
        await session_service.get_session_detail(
            current_user=current_user,
            session_id=session_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    messages = await history_service.get_session_messages(session_id)

    return ChatHistoryResponse(
        session_id=session_id,
        messages=[
            ChatMessageItem(
                role=msg.role.value,
                content=msg.content,
                created_at=msg.created_at,
            )
            for msg in messages
        ],
    )