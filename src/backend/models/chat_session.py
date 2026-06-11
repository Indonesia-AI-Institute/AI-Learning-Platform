from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.backend.models.base import BaseModel


class ChatSession(BaseModel):
    __tablename__ = "chat_sessions"

    student_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    task_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    title = Column(
        String(255), 
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    ended_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    # =========================
    # RELATIONSHIPS
    # =========================

    student = relationship(
        "User",
        back_populates="chat_sessions"
    )

    task = relationship(
        "Task",
        back_populates="chat_sessions",
        lazy="select"
    )

    histories = relationship(
        "ChatHistory",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatHistory.created_at"
    )

    # =========================
    # ANALYTICS RELATIONSHIP
    # =========================

    analytics = relationship(
        "SessionAnalytics",
        back_populates="session",
        cascade="all, delete-orphan",
    )