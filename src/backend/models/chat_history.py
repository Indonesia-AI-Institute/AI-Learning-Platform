from sqlalchemy import (
    Column,
    Text,
    ForeignKey,
    Integer,
    Enum,
    String,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from src.backend.models.base import BaseModel


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageStatus(str, enum.Enum):
    COMPLETED = "completed"
    STREAMING = "streaming"
    ABORTED = "aborted"


class ChatHistory(BaseModel):
    __tablename__ = "chat_histories"

    # =========================
    # CORE REFERENCES
    # =========================

    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,  # assistant messages don't have user
    )

    # =========================
    # MESSAGE CORE
    # =========================

    role = Column(
        Enum(MessageRole, name="message_role_enum"),
        nullable=False,
    )

    content = Column(
        Text,
        nullable=False,
    )

    message_index = Column(
        Integer,
        nullable=True,
        index=True,
    )

    status = Column(
        Enum(MessageStatus, name="message_status_enum"),
        default=MessageStatus.COMPLETED,
        nullable=False,
    )

    # =========================
    # TOKEN & MODEL METADATA
    # =========================

    model_name = Column(
        String,
        nullable=True,
    )

    provider_name = Column(
        String,
        nullable=True,
    )

    input_tokens = Column(
        Integer,
        default=0,
        nullable=False,
    )

    output_tokens = Column(
        Integer,
        default=0,
        nullable=False,
    )

    latency_ms = Column(
        Integer,
        default=0,
        nullable=False,
    )

    token_count = Column(
        Integer,
        nullable=True,  # legacy compatibility (optional)
    )

    message_metadata = Column(
        JSON,
        nullable=True,
    )

    # =========================
    # RELATIONSHIPS
    # =========================

    session = relationship(
        "ChatSession",
        back_populates="histories",
    )