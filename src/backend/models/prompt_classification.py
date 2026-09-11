"""
Stores prompt type classification for each user message.
Populated in parallel with chat response generation.
"""

import uuid

from backend.db.base import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class PromptClassification(Base):
    __tablename__ = "prompt_classifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # FK to the user message in chat_histories
    chat_history_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_histories.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # one classification per message
        index=True,
    )

    # FK for easy querying without joins
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    student_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    task_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    is_direct_answer = Column(Boolean, default=False, nullable=False)
    is_explanation = Column(Boolean, default=False, nullable=False)
    is_step_by_step = Column(Boolean, default=False, nullable=False)
    is_example = Column(Boolean, default=False, nullable=False)
    is_rewrite = Column(Boolean, default=False, nullable=False)
    is_feedback = Column(Boolean, default=False, nullable=False)
    is_summary = Column(Boolean, default=False, nullable=False)
    is_translation = Column(Boolean, default=False, nullable=False)
    is_brainstorm = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ChatSession")
    student = relationship("User")
    task = relationship("Task")