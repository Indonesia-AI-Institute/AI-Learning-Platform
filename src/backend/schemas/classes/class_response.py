from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CourseInfo(BaseModel):
    id: UUID
    title: str

    class Config:
        from_attributes = True


class ClassResponse(BaseModel):
    id: UUID
    course_id: UUID
    name: str
    description: Optional[str]
    is_active: bool
    course: Optional[CourseInfo] = None

    class Config:
        from_attributes = True