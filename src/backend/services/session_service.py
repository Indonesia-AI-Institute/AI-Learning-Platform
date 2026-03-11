from typing import List
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.models.user import User, UserRole
from src.backend.models.chat_session import ChatSession
from src.backend.models.enrollment import Enrollment

from src.backend.repositories.session_repository import SessionRepository
from src.backend.repositories.task_repository import TaskRepository
from src.backend.repositories.course_repository import CourseRepository
from src.backend.repositories.class_repository import ClassRepository
from src.backend.repositories.base_repository import BaseRepository


class SessionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.session_repo = SessionRepository(db)
        self.task_repo = TaskRepository(db)
        self.course_repo = CourseRepository(db)
        self.class_repo = ClassRepository(db)
        self.enrollment_repo = BaseRepository(Enrollment, db)

    # =========================
    # CREATE SESSION (Student Only)
    # =========================

    async def create_session(
        self,
        current_user: User,
        task_id: UUID,
        title: str | None = None,
    ) -> ChatSession:

        if current_user.role != UserRole.STUDENT:
            raise PermissionError("Only students can create sessions.")

        db_task = await self.task_repo.get(task_id)
        if not db_task:
            raise ValueError("Task not found.")

        db_course = await self.course_repo.get(db_task.course_id)
        if not db_course:
            raise ValueError("Course not found.")

        db_class = await self.class_repo.get_by_course_id(db_course.id)
        if not db_class:
            raise ValueError("Class not found.")

        enrollments = await self.enrollment_repo.filter_by(
            student_id=current_user.id,
            class_id=db_class.id,
        )

        if not enrollments:
            raise PermissionError("You are not enrolled in this class.")

        new_session = ChatSession(
            student_id=current_user.id,
            task_id=task_id,
            title=title,
            is_active=True,
        )

        return await self.session_repo.create(new_session)

    # =========================
    # GET MY SESSIONS (Student)
    # =========================

    async def get_my_sessions(
        self,
        current_user: User,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ChatSession]:

        if current_user.role != UserRole.STUDENT:
            raise PermissionError("Only students can access their sessions.")

        return await self.session_repo.get_by_student(
            student_id=current_user.id,
            skip=skip,
            limit=limit,
        )

    # =========================
    # GET SESSION DETAIL WITH ACCESS CHECK
    # =========================

    async def get_session_detail(
        self,
        current_user: User,
        session_id: UUID,
    ) -> ChatSession:

        db_session = await self.session_repo.get(session_id)
        if not db_session:
            raise ValueError("Session not found.")

        db_task = await self.task_repo.get(db_session.task_id)
        db_course = await self.course_repo.get(db_task.course_id)

        if current_user.role == UserRole.STUDENT:
            if db_session.student_id != current_user.id:
                raise PermissionError("Access denied.")
            return db_session

        if current_user.role == UserRole.TEACHER:
            if db_course.teacher_id != current_user.id:
                raise PermissionError("Access denied.")
            return db_session

        raise PermissionError("Access denied.")

    # =========================
    # END SESSION (Student Only)
    # =========================

    async def end_session(
        self,
        current_user: User,
        session_id: UUID,
    ) -> ChatSession:

        db_session = await self.session_repo.get(session_id)
        if not db_session:
            raise ValueError("Session not found.")

        if current_user.role != UserRole.STUDENT:
            raise PermissionError("Only students can end sessions.")

        if db_session.student_id != current_user.id:
            raise PermissionError("You do not own this session.")

        if not db_session.is_active:
            raise ValueError("Session is already ended.")

        return await self.session_repo.update(
            db_session,
            {
                "is_active": False,
                "ended_at": datetime.now(timezone.utc),
            },
        )

    # =========================
    # GET SESSIONS BY TEACHER
    # =========================

    async def get_teacher_sessions(
        self,
        current_user: User,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ChatSession]:

        if current_user.role != UserRole.TEACHER:
            raise PermissionError("Only teachers can access this.")

        return await self.session_repo.get_by_teacher(
            teacher_id=current_user.id,
            skip=skip,
            limit=limit,
        )