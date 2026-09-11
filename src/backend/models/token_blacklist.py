import uuid
from datetime import datetime

from backend.db.base import Base
from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID


class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    token = Column(String, unique=True, nullable=False, index=True)

    revoked_at = Column(DateTime, default=datetime.utcnow)