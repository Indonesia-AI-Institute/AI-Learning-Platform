from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None