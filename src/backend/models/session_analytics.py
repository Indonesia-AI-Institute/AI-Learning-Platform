"""
models/session_analytics.py
===========================

Store LLM usage & metadata per assistant response.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.backend.db.base import Base


class SessionAnalytics(Base):
    __tablename__ = "session_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    chat_session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)

    finish_reason = Column(String, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())

    # relationships
    session = relationship(
        "ChatSession", 
        back_populates="analytics")
    user = relationship(
        "User"
        )