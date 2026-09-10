from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CourseCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    is_active: bool = True
 
    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Course title is required and cannot be empty.")
        return stripped