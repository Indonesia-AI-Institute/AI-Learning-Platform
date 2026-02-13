"""
chat_routes.py
==============

Chat API Routes.

Fungsi:
- Endpoint komunikasi chatbot
- Handle SSE streaming response
- Handle non-stream response (testing / fallback)

Scope Saat Ini:
✔ Student kirim prompt
✔ Return assistant response
✔ Streaming SSE support
✔ Banlist guardrail via ChatService

Future:
- Task Context Injection
- Chat History Storage
- Prompt Scoring
- Multi Model Selection
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from api.deps import get_chat_service
from services.chat_service import ChatService

from schemas.chat.chat_request import ChatRequest
from schemas.chat.chat_response import ChatResponse

from utils.streaming_utils import sse_stream_wrapper


router = APIRouter()


# =========================================================
# STREAMING CHAT (PRIMARY MODE - SSE)
# =========================================================
@router.post("/stream")
async def stream_chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Streaming Chat Endpoint (SSE).

    Flow:
    Client → POST prompt
    Server → SSE token stream
    """
    chat_history_dicts = None
    if request.chat_history:
        chat_history_dicts = [msg.model_dump() for msg in request.chat_history]

    async def event_stream():
        async for chunk in chat_service.stream_chat(
            user_prompt=request.user_prompt,
            system_prompt=request.system_prompt,
            chat_history=chat_history_dicts,
        ):
            yield chunk

    return StreamingResponse(
        sse_stream_wrapper(event_stream()),
        media_type="text/event-stream",
    )


# =========================================================
# NON STREAM CHAT (SECONDARY / TESTING MODE)
# =========================================================
@router.post("/generate", response_model=ChatResponse)
async def generate_chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Non-stream chat endpoint.

    Berguna untuk:
    - Testing
    - Postman
    - Debugging
    """

    # ── Konversi chat_history dari ChatMessage ke dict ──
    chat_history_dicts = None
    if request.chat_history:
        chat_history_dicts = [msg.model_dump() for msg in request.chat_history]

    # Panggil ChatService dengan format yang sudah benar
    response = await chat_service.chat(
        user_prompt=request.user_prompt,
        system_prompt=request.system_prompt,
        chat_history=chat_history_dicts,
    )

    return ChatResponse(**response)