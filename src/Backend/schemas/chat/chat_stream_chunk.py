"""
chat_stream_chunk.py
====================

Schema untuk streaming chunk data via SSE.

Digunakan untuk:
- Streaming token response dari LLM
- Standardisasi format SSE message

Saat ini fokus:
✔ Token streaming
✔ Done event
✔ Error event

Future Ready:
- Usage token summary
- Reasoning trace
- Latency metrics
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


# =========================================================
# STREAM EVENT TYPES
# =========================================================

StreamEventType = Literal[
    "token",
    "done",
    "error"
]


# =========================================================
# STREAM CHUNK SCHEMA
# =========================================================

class ChatStreamChunk(BaseModel):
    """
    Standard SSE chunk format.
    """

    event: StreamEventType = Field(
        ...,
        description="Jenis streaming event"
    )

    data: Optional[str] = Field(
        None,
        description="Isi token / message streaming"
    )

    error_message: Optional[str] = Field(
        None,
        description="Error message jika event = error"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "event": "token",
                    "data": "Artificial "
                },
                {
                    "event": "token",
                    "data": "Intelligence "
                },
                {
                    "event": "done",
                    "data": None
                },
                {
                    "event": "error",
                    "error_message": "LLM timeout"
                }
            ]
        }
