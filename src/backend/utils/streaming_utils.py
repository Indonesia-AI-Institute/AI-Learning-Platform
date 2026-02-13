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

from schemas.chat.chat_stream_chunk import ChatStreamChunk


# =========================================================
# CORE SSE FORMATTER (Transport Layer)
# =========================================================

def format_sse(data: dict) -> str:
    """
    Convert dict -> SSE formatted string.

    SSE Standard:
    data: <json>
    """
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


# =========================================================
# DOMAIN EVENT BUILDERS
# =========================================================

def build_token_event(token: str) -> str:
    """
    Build token streaming event.
    """

    chunk = ChatStreamChunk(
        event="token",
        data=token
    )

    return format_sse(chunk.model_dump())


def build_done_event() -> str:
    """
    Build stream completion event.
    """

    chunk = ChatStreamChunk(
        event="done"
    )

    return format_sse(chunk.model_dump())


def build_error_event(message: str) -> str:
    """
    Build stream error event.
    """

    chunk = ChatStreamChunk(
        event="error",
        error_message=message
    )

    return format_sse(chunk.model_dump())


# =========================================================
# MAIN STREAM WRAPPER (SAFE STREAM EXECUTION)
# =========================================================

async def sse_stream_wrapper(
    token_generator: AsyncGenerator[str, None]
) -> AsyncGenerator[str, None]:
    """
    Wrap token generator -> SSE formatted stream.

    Responsibilities:
    - Convert token -> SSE token event
    - Handle stream completion
    - Handle exception -> error event

    Digunakan di:
    - Chat route layer
    """

    try:
        async for token in token_generator:
            yield build_token_event(token)

        # Send done event
        yield build_done_event()

    except Exception as e:
        yield build_error_event(str(e))