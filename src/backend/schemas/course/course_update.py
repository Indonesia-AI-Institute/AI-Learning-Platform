from pydantic import BaseModel, Field
from typing import Optional

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None