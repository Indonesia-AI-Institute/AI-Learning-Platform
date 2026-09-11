import enum

from backend.models.base import BaseModel
from sqlalchemy import (
    JSON,
    Column,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


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

    session = relationship(
        "ChatSession",
        back_populates="histories",
    )