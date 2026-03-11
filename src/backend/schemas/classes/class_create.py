from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class ClassCreate(BaseModel):
    course_id: UUID
    name: str
    description: Optional[str] = None