from uuid import UUID
from datetime import datetime
from typing import List

from pydantic import BaseModel


class ChatMessageItem(BaseModel):
    role: str
    content: str
    created_at: datetime


class ChatHistoryResponse(BaseModel):
    session_id: UUID
    messages: List[ChatMessageItem]