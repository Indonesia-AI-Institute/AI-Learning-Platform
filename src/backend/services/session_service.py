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

from src.backend.services.session_analytics_service import SessionAnalyticsService


class SessionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.session_repo = SessionRepository(db)
        self.task_repo = TaskRepository(db)
        self.course_repo = CourseRepository(db)
        self.class_repo = ClassRepository(db)
        self.enrollment_repo = BaseRepository(Enrollment, db)
        self.analytics_service = SessionAnalyticsService(db)

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

        # FIX: get all classes for this course, then find one the student is enrolled in
        # instead of get_by_course_id which fails if course has multiple classes
        classes = await self.class_repo.get_by_course(course_id=db_course.id)
        if not classes:
            raise ValueError("No classes found for this course.")

        class_ids = [cls.id for cls in classes]

        # Find enrollment for this student in any of the course's classes
        enrolled_class = None
        for class_id in class_ids:
            enrollments = await self.enrollment_repo.filter_by(
                student_id=current_user.id,
                class_id=class_id,
            )
            if enrollments:
                enrolled_class = class_id
                break

        if not enrolled_class:
            raise PermissionError("You are not enrolled in this course.")

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
    # GET SESSIONS BY TASK (Student)
    # =========================

    async def get_sessions_by_task(
        self,
        current_user: User,
        task_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ChatSession]:

        if current_user.role != UserRole.STUDENT:
            raise PermissionError("Only students can access their sessions.")

        db_task = await self.task_repo.get(task_id)
        if not db_task:
            raise ValueError("Task not found.")

        return await self.session_repo.get_by_student_and_task(
            student_id=current_user.id,
            task_id=task_id,
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

        await self.analytics_service.finalize_session_analytics(
            session=db_session,
        )

        return await self.session_repo.update(
            db_session,
            {
                "is_active": False,
                "ended_at": datetime.now(timezone.utc),
            },
        )

    # =========================
    # RESUME SESSION (Student Only)
    # =========================

    async def resume_session(
        self,
        current_user: User,
        session_id: UUID,
    ) -> ChatSession:

        db_session = await self.session_repo.get(session_id)
        if not db_session:
            raise ValueError("Session not found.")

        if current_user.role != UserRole.STUDENT:
            raise PermissionError("Only students can resume sessions.")

        if db_session.student_id != current_user.id:
            raise PermissionError("You do not own this session.")

        if db_session.is_active:
            raise ValueError("Session is already active.")

        # TODO: RAG context injection
        # Saat RAG sudah tersedia, inject summary dari chat history
        # sebagai context awal LLM sebelum session di-reactivate.

        return await self.session_repo.update(
            db_session,
            {
                "is_active": True,
                "ended_at": None,
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