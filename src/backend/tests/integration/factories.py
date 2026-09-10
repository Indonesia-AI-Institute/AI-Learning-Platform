"""
Shared test-data builders for integration tests. Insert directly via
db_session (fast, decouples fixture setup from the endpoints under test)
rather than chaining HTTP calls, per the enrich-integration-tests skill.
"""

from backend.auth.security import create_access_token, hash_password
from backend.models.class_model import Class
from backend.models.course import Course
from backend.models.enrollment import Enrollment
from backend.models.task import Task
from backend.models.user import User, UserRole


def token_for(user: User) -> str:
    return create_access_token(user_id=str(user.id), role=user.role.value)


def auth_headers(user: User) -> dict:
    return {"Authorization": f"Bearer {token_for(user)}"}


async def create_teacher(db, suffix: str) -> User:
    user = User(
        full_name=f"Teacher {suffix}",
        email=f"teacher-{suffix}@example.com",
        hashed_password=hash_password("x"),
        role=UserRole.TEACHER,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def create_student(db, suffix: str) -> User:
    user = User(
        full_name=f"Student {suffix}",
        email=f"student-{suffix}@example.com",
        hashed_password=hash_password("x"),
        role=UserRole.STUDENT,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def create_course(db, teacher: User, suffix: str = "", is_active: bool = True) -> Course:
    course = Course(
        teacher_id=teacher.id,
        title=f"Course {suffix}" if suffix else "Course",
        is_active=is_active,
    )
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course


async def create_class(db, course: Course, suffix: str = "", is_active: bool = True) -> Class:
    klass = Class(
        course_id=course.id,
        name=f"Class {suffix}" if suffix else "Class",
        is_active=is_active,
    )
    db.add(klass)
    await db.commit()
    await db.refresh(klass)
    return klass


async def create_task(db, course: Course, klass: Class | None = None, suffix: str = "") -> Task:
    task = Task(
        course_id=course.id,
        class_id=klass.id if klass else None,
        title=f"Task {suffix}" if suffix else "Task",
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def create_enrollment(db, student: User, klass: Class) -> Enrollment:
    enrollment = Enrollment(student_id=student.id, class_id=klass.id)
    db.add(enrollment)
    await db.commit()
    await db.refresh(enrollment)
    return enrollment
