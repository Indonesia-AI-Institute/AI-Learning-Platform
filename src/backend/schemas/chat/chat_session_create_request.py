"""
chat_session_create_request.py
==============================

Pydantic schema for creating a new Chat Session.

Used by:
- POST /chat/sessions/task/{task_id}
"""

from typing import Optional
from pydantic import BaseModel, Field


class ChatSessionCreateRequest(BaseModel):
    """
    Request body for creating a new chat session.
    task_id is passed via URL path, not body.
    """

    title: Optional[str] = Field(
        None,
        max_length=255,
        description="Optional title for this chat session",
        example="Sesi belajar neural network"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Sesi belajar neural network"
            }
        }