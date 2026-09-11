from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ClassCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    course_id: str
    is_active: bool = True
 
    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Class name is required and cannot be empty.")
        return stripped