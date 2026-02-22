"""
chat_routes.py
==============

Chat API Routes (Split Agent Architecture).

Endpoints:
✔ /chat/direct/*
✔ /chat/socratic/*
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from api.deps import get_chat_service
from services.chat_service import ChatService

from schemas.chat.chat_request import ChatRequest
from schemas.chat.chat_response import ChatResponse

from utils.streaming_utils import sse_stream_wrapper


router = APIRouter(prefix="/chat", tags=["Chat"])


# =========================================================
# INTERNAL HELPER
# =========================================================

def build_messages(request: ChatRequest):
    messages = []

    if request.system_prompt:
        messages.append({
            "role": "system",
            "content": request.system_prompt,
        })

    messages.extend([
        msg.model_dump() for msg in request.messages
    ])

    return messages


# =========================================================
# DIRECT AGENT
# =========================================================

@router.post("/direct/stream")
async def stream_direct_chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
):
    messages = build_messages(request)

    async def event_stream():
        async for chunk in chat_service.stream_generate(
            agent_type="direct_tutor",
            messages=messages,
        ):
            yield chunk

    return StreamingResponse(
        sse_stream_wrapper(event_stream()),
        media_type="text/event-stream",
    )


@router.post("/direct/generate", response_model=ChatResponse)
async def generate_direct_chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
):
    messages = build_messages(request)

    response = await chat_service.generate(
        agent_type="direct_tutor",
        messages=messages,
    )

    return ChatResponse(
        response_text=response["content"]
    )

# =========================================================
# SOCRATIC AGENT
# =========================================================

@router.post("/socratic/stream")
async def stream_socratic_chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
):
    messages = build_messages(request)

    async def event_stream():
        async for chunk in chat_service.stream_generate(
            agent_type="socratic_tutor",
            messages=messages,
        ):
            yield chunk

    return StreamingResponse(
        sse_stream_wrapper(event_stream()),
        media_type="text/event-stream",
    )


@router.post("/socratic/generate", response_model=ChatResponse)
async def generate_socratic_chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
):
    messages = build_messages(request)

    response = await chat_service.generate(
        agent_type="socratic_tutor",
        messages=messages,
    )

    return ChatResponse(
        response_text=response["content"]
    )