from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ClassUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    is_active: Optional[bool] = None
 
    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        stripped = v.strip()
        if not stripped:
            raise ValueError("Class name cannot be empty.")
        return stripped