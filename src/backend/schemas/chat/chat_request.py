"""
chat_request.py
===============

Pydantic schema for Chat Request (Split Agent Architecture).

Used by:
- /chat/direct/*
- /chat/sessions/{session_id}/stream
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
        description="Full conversation history"
    )

    system_prompt: Optional[str] = Field(
        None,
        description="Optional system prompt override"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {
                        "role": "user",
                        "content": "Explain what is a neural network"
                    }
                ]
            }
        }