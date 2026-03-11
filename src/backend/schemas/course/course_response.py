from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class CourseResponse(BaseModel):
    id: UUID
    teacher_id: UUID
    title: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True