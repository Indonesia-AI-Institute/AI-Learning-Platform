"""
Aggregated analytics per chat session.
Populated when session is ended via finalize_session_analytics().
"""

import uuid

from backend.db.base import Base
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class SessionAnalytics(Base):
    __tablename__ = "session_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    chat_session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # one analytics record per session
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    task_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
    )

    prompt_tokens = Column(Integer, default=0, nullable=False)
    completion_tokens = Column(Integer, default=0, nullable=False)
    total_tokens = Column(Integer, default=0, nullable=False)

    total_prompts = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Total number of messages sent by student in this session",
    )

    avg_prompt_length = Column(
        Float,
        default=0.0,
        nullable=False,
        comment="Average character length of student prompts",
    )

    session_duration_seconds = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Duration from first message to last message in seconds",
    )

    finish_reason = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    session = relationship("ChatSession", back_populates="analytics")
    user = relationship("User")
    task = relationship("Task")