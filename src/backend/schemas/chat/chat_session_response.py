from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ChatSessionResponse(BaseModel):
    id: UUID
    student_id: UUID
    task_id: UUID
    title: str | None
    is_active: bool
    ended_at: datetime | None

    class Config:
        from_attributes = True