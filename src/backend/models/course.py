"""
models/course.py
================

Course Domain Model
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.backend.db.base import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    teacher_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    title = Column(String(255), nullable=False)
    description = Column(String, nullable=True)

    is_active = Column(Boolean, default=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    teacher = relationship(
        "User",
        back_populates="course"
    )

    classes = relationship(
        "Class",
        back_populates="course"
    )

    tasks = relationship (
        "Task", 
        back_populates="course", 
        cascade="all, delete-orphan"
    )