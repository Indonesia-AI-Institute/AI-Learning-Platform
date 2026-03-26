from pydantic import BaseModel, Field
from typing import Optional


class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None