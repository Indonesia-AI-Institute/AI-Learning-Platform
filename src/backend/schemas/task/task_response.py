"""
is_active wajib ada di response agar:
1. Frontend bisa menampilkan status active/inactive
2. Toggle di edit page bisa pre-fill nilai yang benar
3. Auto-deactivate due date reflect ke UI
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ClassInfo(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    is_active: bool                        # FIX: field ini wajib ada
    course_id: UUID
    class_id: Optional[UUID] = None
    class_info: Optional[ClassInfo] = None

    class Config:
        from_attributes = True