from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class ClassResponse(BaseModel):
    id: UUID
    course_id: UUID
    name: str
    description: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True