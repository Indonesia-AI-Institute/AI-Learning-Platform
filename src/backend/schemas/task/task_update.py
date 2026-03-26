from pydantic import BaseModel, Field
from typing import Optional

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_active: bool | None = None