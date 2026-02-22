"""
chat_request.py
===============

Pydantic schema for Chat Request (Split Agent Architecture).

Used by:
- /chat/direct/*
- /chat/socratic/*

Architecture:
✔ Stateless
✔ Multi-turn ready
✔ Socratic ready
✔ Streaming handled by endpoint
"""

from typing import List, Optional
from pydantic import BaseModel, Field


# =========================================================
# CHAT MESSAGE ITEM
# =========================================================

class ChatMessage(BaseModel):
    """
    Single message in conversation history.
    """

    role: str = Field(
        ...,
        description="Role of the message sender (user | assistant | system)",
        example="user"
    )

    content: str = Field(
        ...,
        description="Message content text",
        example="Explain machine learning in simple terms."
    )


# =========================================================
# MAIN CHAT REQUEST
# =========================================================

class ChatRequest(BaseModel):
    """
    Chat request for Direct or Socratic endpoint.
    Agent selection is handled by URL path.
    """

    messages: List[ChatMessage] = Field(
        ...,
        description="Full conversation history (stateless)"
    )

    system_prompt: Optional[str] = Field(
        None,
        description="Optional system prompt override"
    )

    # =====================================================
    # FUTURE EXTENSIONS (SAFE)
    # =====================================================

    task_id: Optional[str] = Field(
        None,
        description="Optional task identifier"
    )

    session_id: Optional[str] = Field(
        None,
        description="Optional session identifier"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {
                        "role": "user",
                        "content": "Explain what is a neural network"
                    }
                ],
                "task_id": "task_123",
                "session_id": "session_abc"
            }
        }
