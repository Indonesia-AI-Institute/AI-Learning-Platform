from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.backend.models.base import BaseModel, SoftDeleteMixin


"""
models/class_model.py
=====================
Class Domain Model
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.backend.db.base import Base


class Class(Base):
    __tablename__ = "classes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Parent Course
    course_id = Column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False
    )

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    # Eagerly load the related Course to avoid async lazy loading after the DB session is closed.
    # Using "joined" loading ensures the Course data is fetched in the same query, preventing
    # MissingGreenlet errors when FastAPI serializes the response outside the async session.
    course = relationship(
        "Course",
        back_populates="classes",
        lazy="joined",
    )
    enrollments = relationship(
        "Enrollment", 
        back_populates="classes", 
        cascade="all, delete-orphan"
    )