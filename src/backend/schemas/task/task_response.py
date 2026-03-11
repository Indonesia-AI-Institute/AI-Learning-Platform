from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    course_id: UUID

    model_config = {
        "from_attributes": True
    }