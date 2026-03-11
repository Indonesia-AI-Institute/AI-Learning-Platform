from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.backend.models.base import BaseModel, SoftDeleteMixin


class Task(BaseModel, SoftDeleteMixin):
    __tablename__ = "tasks"

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    due_date = Column(
        DateTime(timezone=True),
        nullable=True
    )

    course_id = Column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # =========================
    # RELATIONSHIPS
    # =========================

    course = relationship(
        "Course",
        back_populates="tasks"
    )

    chat_sessions = relationship(
        "ChatSession",
        back_populates="task",
        cascade="all, delete-orphan"
    )