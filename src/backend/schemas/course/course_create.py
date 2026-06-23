from typing import Optional
from pydantic import BaseModel, field_validator
 
 
class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    is_active: bool = True
 
    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Course title is required and cannot be empty.")
        return stripped