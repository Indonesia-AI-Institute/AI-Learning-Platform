import uuid

from backend.db.base import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Class(Base):
    __tablename__ = "classes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    course_id = Column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False
    )

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    task = relationship(
        "Task",
        back_populates="classes"
    )

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