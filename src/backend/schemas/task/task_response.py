from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class ClassInfo(BaseModel):
    id: UUID
    name: str

    model_config = {"from_attributes": True}


class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    course_id: UUID

    # Populated via service layer, not direct ORM relation
    class_info: Optional[ClassInfo] = None

    model_config = {"from_attributes": True}