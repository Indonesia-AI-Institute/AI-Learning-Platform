"""
chat_request.py
===============

Pydantic schema untuk Chat Request dari frontend.

Digunakan oleh:
- Chat REST endpoint
- Chat SSE endpoint

Saat ini fokus:
✔ Text prompt only
✔ Raw prompt passthrough
✔ Stateless ready
✔ SSE ready

Future Ready:
- Task based tracking
- Multi session tracking
- Model selection
"""

from typing import List, Optional
from pydantic import BaseModel, Field


# =========================================================
# CHAT MESSAGE HISTORY ITEM
# =========================================================

class ChatMessage(BaseModel):
    """
    Single message dalam chat history.
    """

    role: str = Field(
        ...,
        description="Role message: system | user | assistant",
        example="user"
    )

    content: str = Field(
        ...,
        description="Isi message text",
        example="Explain machine learning in simple terms."
    )


# =========================================================
# MAIN CHAT REQUEST
# =========================================================

class ChatRequest(BaseModel):
    """
    Main request schema untuk Chat API.
    """

    user_prompt: str = Field(
        ...,
        description="Prompt utama dari user",
        example="Apa itu Large Language Model?"
    )

    system_prompt: Optional[str] = Field(
        None,
        description="Optional system instruction untuk AI behavior"
    )

    chat_history: Optional[List[ChatMessage]] = Field(
        None,
        description="Optional chat history untuk multi-turn conversation"
    )

    # =====================================================
    # FUTURE READY FIELDS (SAFE UNTUK SEKARANG)
    # =====================================================

    task_id: Optional[str] = Field(
        None,
        description="Future: Task identifier untuk logging per task"
    )

    session_id: Optional[str] = Field(
        None,
        description="Future: Session identifier untuk multi session chat"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_prompt": "Explain what is neural network",
                "system_prompt": "You are a helpful AI tutor.",
                "chat_history": [
                    {
                        "role": "user",
                        "content": "What is AI?"
                    },
                    {
                        "role": "assistant",
                        "content": "AI is Artificial Intelligence..."
                    }
                ]
            }
        }