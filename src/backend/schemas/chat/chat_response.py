"""
chat_response.py
================

Schema untuk non-streaming Chat Response.

Digunakan untuk:
- REST Chat endpoint
- Testing endpoint
- Debug endpoint

Saat ini fokus:
✔ Assistant response text
✔ Optional usage metadata
✔ Optional finish reason

Tidak expose:
❌ Raw provider response
❌ Internal LLM metadata
"""

from typing import Optional, Dict
from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    """
    Standard response schema untuk chat completion.
    """

    response_text: str = Field(
        ...,
        description="Final response text dari assistant"
    )

    usage: Optional[Dict[str, int]] = Field(
        None,
        description="Token usage metadata jika tersedia"
    )

    finish_reason: Optional[str] = Field(
        None,
        description="Reason kenapa generation selesai"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "response_text": "Neural network adalah model machine learning...",
                "usage": {
                    "prompt_tokens": 120,
                    "completion_tokens": 80,
                    "total_tokens": 200
                },
                "finish_reason": "stop"
            }
        }
