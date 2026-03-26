"""
streaming_utils.py
==================

Helper utilities untuk format SSE streaming response.

Digunakan oleh:
- Chat streaming API route
- LLM streaming pipeline

Tujuan:
- Standardisasi SSE format output
- Convert ChatStreamChunk -> SSE string
- Handle done / error events
- Future ready untuk reasoning / scoring / multi-pass event

SSE Format Standard:
data: <json>\n\n
"""

import json
from typing import AsyncGenerator

from src.backend.schemas.chat.chat_stream_chunk import ChatStreamChunk


# =========================================================
# CORE SSE FORMATTER
# =========================================================

def format_sse(data: dict) -> str:
    """
    Convert dict -> SSE formatted string.

    SSE Standard:
    data: <json>\n\n
    """
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


# =========================================================
# DOMAIN EVENT BUILDERS
# =========================================================

def build_token_event(token: str) -> str:
    chunk = ChatStreamChunk(
        event="token",
        data=token
    )
    return format_sse(chunk.model_dump())


def build_done_event() -> str:
    chunk = ChatStreamChunk(
        event="done"
    )
    return format_sse(chunk.model_dump())


def build_error_event(message: str) -> str:
    chunk = ChatStreamChunk(
        event="error",
        error_message=message
    )
    return format_sse(chunk.model_dump())


# =========================================================
# SAFE STREAM WRAPPER
# =========================================================

async def sse_stream_wrapper(generator):

    async for chunk in generator:
        yield f"data: {chunk}\n\n"

    yield "data: [DONE]\n\n"
