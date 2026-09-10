"""
Semua field optional (PATCH-style), kecuali title yang jika
disertakan tidak boleh kosong.
is_active wajib ada agar toggle active/inactive berfungsi.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_validator


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    is_active: Optional[bool] = None       # FIX: wajib ada untuk toggle
    class_id: Optional[str] = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        stripped = v.strip()
        if not stripped:
            raise ValueError("Task title cannot be empty.")
        return stripped

    @field_validator("description")
    @classmethod
    def strip_description(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        stripped = v.strip()
        return stripped if stripped else None