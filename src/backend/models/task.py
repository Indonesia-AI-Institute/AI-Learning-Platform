"""
Tambah kolom is_active yang sebelumnya tidak ada.
Ini adalah root cause dari semua bug:
- Task list hilang (500 dari auto_deactivate_overdue)
- Create task gagal (TypeError: is_active invalid keyword)
- Toggle active/inactive tidak berfungsi
"""

from backend.models.base import BaseModel
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship


class Task(BaseModel):
    __tablename__ = "tasks"

    course_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    class_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("classes.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    title = Column(String(255), nullable=False)

    description = Column(Text, nullable=True)

    due_date = Column(DateTime(timezone=True), nullable=True)

    # Kolom yang hilang — ini root cause semua bug
    is_active = Column(Boolean, default=True, nullable=False)

    classes = relationship(
        "Class",
        back_populates="task",
        lazy="joined",
    )

    course = relationship(
        "Course", 
        back_populates="task",
    )
    chat_sessions = relationship(
        "ChatSession",
        back_populates="task",
        cascade="all, delete-orphan",
    )