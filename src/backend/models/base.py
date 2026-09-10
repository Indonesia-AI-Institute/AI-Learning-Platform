import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from backend.db.base import Base


class UUIDMixin:
    """
    Provide UUID primary key for all models.
    """
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )


class TimestampMixin:
    """
    Provide created_at and updated_at fields (UTC timezone-aware).
    """
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class SoftDeleteMixin:
    """
    Provide soft delete capability.
    Only use this mixin for models that need soft delete.
    """
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False
    )

    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)


class BaseModel(Base, UUIDMixin, TimestampMixin):
    """
    Base model that includes:
    - UUID primary key
    - created_at
    - updated_at
    """
    __abstract__ = True