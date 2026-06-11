"""
api/v1/chat_routes.py
"""

from uuid import UUID
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.backend.utils.role_guard import RoleGuard
from src.backend.api.deps import get_db, get_chat_service
from src.backend.services.prompt_classification_service import PromptClassificationService
from src.backend.llm.services.llm_service import LLMService
from src.backend.services.session_service import SessionService
from src.backend.services.chat_history_service import ChatHistoryService
from src.backend.services.chat_service import ChatService
from src.backend.services.conversation_service import ConversationService

from src.backend.models.user import User, UserRole
from src.backend.models.chat_session import ChatSession
from src.backend.models.task import Task
from src.backend.models.course import Course

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
    return ConversationService(
        session_service=SessionService(db),
        history_service=ChatHistoryService(db),
        chat_service=chat_service,
        classification_service=PromptClassificationService(db),
        llm_service=LLMService(),
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
            messages.append({"role": "system", "content": request.system_prompt})
        messages.extend([msg.model_dump() for msg in request.messages])
        async for event in chat_service.stream_generate(agent_type="direct_tutor", messages=messages):
            if event["type"] == "token":
                yield event["content"]

    return StreamingResponse(sse_stream_wrapper(event_stream()), media_type="text/event-stream")


@router.post("/direct/generate", response_model=ChatResponse)
async def generate_direct_chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
):
    messages = []
    if request.system_prompt:
        messages.append({"role": "system", "content": request.system_prompt})
    messages.extend([msg.model_dump() for msg in request.messages])
    response = await chat_service.generate(agent_type="direct_tutor", messages=messages)
    return ChatResponse(response_text=response["content"])


# =========================================================
# CREATE SESSION (Student)
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
# PENTING: route static "/my" harus SEBELUM route dynamic "/{session_id}"
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
        return await service.get_my_sessions(current_user=current_user, skip=skip, limit=limit)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# =========================================================
# GET SESSIONS BY TASK (Student)
# PENTING: route "/task/{task_id}" harus SEBELUM "/{session_id}"
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
        return await service.get_sessions_by_task(
            current_user=current_user,
            task_id=task_id,
            skip=skip,
            limit=limit,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# =========================================================
# GET SINGLE SESSION BY ID (Student)
# Dipakai chat room page — lebih efisien dari getMySessions().find()
# =========================================================

@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_session_by_id(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleGuard([UserRole.STUDENT])),
):
    service = SessionService(db)
    try:
        return await service.get_session_detail(
            current_user=current_user,
            session_id=session_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# =========================================================
# STREAM SESSION CHAT (Student)
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

    return StreamingResponse(sse_stream_wrapper(event_stream()), media_type="text/event-stream")


# =========================================================
# END SESSION (Student)
# =========================================================

@router.post("/sessions/{session_id}/end", response_model=ChatSessionResponse)
async def end_chat_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleGuard([UserRole.STUDENT])),
):
    service = SessionService(db)
    try:
        return await service.end_session(current_user=current_user, session_id=session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# =========================================================
# RESUME SESSION (Student)
# =========================================================

@router.post("/sessions/{session_id}/resume", response_model=ChatSessionResponse)
async def resume_chat_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleGuard([UserRole.STUDENT])),
):
    service = SessionService(db)
    try:
        return await service.resume_session(current_user=current_user, session_id=session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# =========================================================
# AUTO-END SESSION (Student — called on page unmount)
# =========================================================

@router.post("/sessions/{session_id}/auto-end", response_model=ChatSessionResponse)
async def auto_end_chat_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleGuard([UserRole.STUDENT])),
):
    """
    Dipanggil otomatis oleh frontend saat student navigasi keluar chat room.
    Graceful: tidak error jika session sudah ended.
    """
    service = SessionService(db)
    try:
        return await service.end_session(current_user=current_user, session_id=session_id)
    except ValueError:
        # Session mungkin sudah ended — tidak apa-apa
        db_session = await service.session_repo.get(session_id)
        if db_session:
            return db_session
        raise HTTPException(status_code=404, detail="Session not found.")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# =========================================================
# DELETE SESSION (Student)
# =========================================================

@router.delete("/sessions/{session_id}", status_code=204)
async def delete_chat_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleGuard([UserRole.STUDENT])),
):
    service = SessionService(db)
    try:
        await service.delete_session(current_user=current_user, session_id=session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# =========================================================
# GET CHAT HISTORY (Student)
# =========================================================

@router.get("/sessions/{session_id}/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleGuard([UserRole.STUDENT])),
):
    service = SessionService(db)
    history_service = ChatHistoryService(db)

    try:
        await service.get_session_detail(current_user=current_user, session_id=session_id)
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


# =========================================================
# TEACHER — GET STUDENT SESSIONS (with task title)
# =========================================================

@router.get("/teacher/student/{student_id}/sessions")
async def get_student_sessions_for_teacher(
    student_id: UUID,
    task_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleGuard([UserRole.TEACHER])),
):
    """Teacher: lihat semua chat session student dalam course yang diajar."""
    stmt = (
        select(ChatSession)
        .join(Task, ChatSession.task_id == Task.id)
        .join(Course, Task.course_id == Course.id)
        .options(selectinload(ChatSession.task))
        .where(
            ChatSession.student_id == student_id,
            Course.teacher_id == current_user.id,
        )
    )

    if task_id:
        stmt = stmt.where(ChatSession.task_id == task_id)

    stmt = stmt.order_by(ChatSession.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(stmt)
    sessions = result.scalars().all()

    return [
        {
            "id": str(s.id),
            "student_id": str(s.student_id),
            "task_id": str(s.task_id),
            "task_title": s.task.title if s.task else None,
            "title": s.title,
            "is_active": s.is_active,
            "created_at": s.created_at.isoformat(),
            "ended_at": s.ended_at.isoformat() if s.ended_at else None,
        }
        for s in sessions
    ]


# =========================================================
# TEACHER — GET SESSION HISTORY
# =========================================================

@router.get("/teacher/sessions/{session_id}/history", response_model=ChatHistoryResponse)
async def get_session_history_for_teacher(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleGuard([UserRole.TEACHER])),
):
    """Teacher: lihat full chat history dari session manapun di course mereka."""
    # Verifikasi session ada di course yang diajar teacher
    stmt = (
        select(ChatSession)
        .join(Task, ChatSession.task_id == Task.id)
        .join(Course, Task.course_id == Course.id)
        .where(
            ChatSession.id == session_id,
            Course.teacher_id == current_user.id,
        )
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found or access denied.")

    history_service = ChatHistoryService(db)
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