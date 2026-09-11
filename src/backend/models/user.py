import enum

from backend.models.base import BaseModel, SoftDeleteMixin
from sqlalchemy import Column, Enum, String
from sqlalchemy.orm import relationship


class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"


class User(BaseModel, SoftDeleteMixin):
    __tablename__ = "users"

    full_name = Column(String(255), nullable=False)

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    hashed_password = Column(String(255), nullable=False)

    role = Column(
        Enum(UserRole, name="user_role_enum"),
        nullable=False
    )

    # Teacher → courses
    course = relationship(
        "Course",
        back_populates="teacher",
        cascade="all, delete-orphan"
    )

    # Student → enroll
    enrollments = relationship(
        "Enrollment",
        back_populates="student",
        cascade="all, delete-orphan"
    )

    # Student → chat
    chat_sessions = relationship(
        "ChatSession",
        back_populates="student",
        cascade="all, delete-orphan"
    )