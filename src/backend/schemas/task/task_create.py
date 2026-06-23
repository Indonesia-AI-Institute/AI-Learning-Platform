"""
schemas/task/task_create.py
===========================
Title wajib diisi dan tidak boleh berupa string kosong/whitespace.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_validator


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    is_active: bool = True

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Task title is required and cannot be empty.")
        return stripped

    @field_validator("description")
    @classmethod
    def strip_description(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        stripped = v.strip()
        return stripped if stripped else None