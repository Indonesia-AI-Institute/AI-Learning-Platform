from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class TeacherInfo(BaseModel):
    id: UUID
    full_name: str

    class Config:
        from_attributes = True


class CourseResponse(BaseModel):
    id: UUID
    teacher_id: UUID
    title: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    teacher: Optional[TeacherInfo] = None

    class Config:
        from_attributes = True