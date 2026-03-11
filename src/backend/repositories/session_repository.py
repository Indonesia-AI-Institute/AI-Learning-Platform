from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.backend.models.chat_session import ChatSession
from src.backend.models.task import Task
from src.backend.models.course import Course
from src.backend.repositories.base_repository import BaseRepository


class SessionRepository(BaseRepository[ChatSession]):
    def __init__(self, db: AsyncSession):
        super().__init__(ChatSession, db)

    # =========================
    # GET SESSIONS BY STUDENT
    # =========================

    async def get_by_student(
        self,
        student_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ChatSession]:

        stmt = (
            select(ChatSession)
            .where(ChatSession.student_id == student_id)
            .order_by(ChatSession.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    # =========================
    # GET SESSIONS BY TASK
    # =========================

    async def get_by_task(
        self,
        task_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ChatSession]:

        stmt = (
            select(ChatSession)
            .where(ChatSession.task_id == task_id)
            .order_by(ChatSession.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    # =========================
    # GET ACTIVE SESSION OF STUDENT FOR TASK
    # =========================

    async def get_active_session(
        self,
        student_id: UUID,
        task_id: UUID,
    ) -> Optional[ChatSession]:

        stmt = (
            select(ChatSession)
            .where(
                ChatSession.student_id == student_id,
                ChatSession.task_id == task_id,
                ChatSession.is_active.is_(True),
            )
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # =========================
    # GET SESSIONS BY TEACHER
    # Teacher is on Course, not Class
    # =========================

    async def get_by_teacher(
        self,
        teacher_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ChatSession]:

        stmt = (
            select(ChatSession)
            .join(Task, ChatSession.task_id == Task.id)
            .join(Course, Task.course_id == Course.id)
            .where(Course.teacher_id == teacher_id)
            .order_by(ChatSession.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    # =========================
    # GET ONE SESSION BY STUDENT
    # =========================

    async def get_one_by_student(
        self,
        session_id: UUID,
        student_id: UUID,
    ) -> Optional[ChatSession]:

        stmt = (
            select(ChatSession)
            .where(
                ChatSession.id == session_id,
                ChatSession.student_id == student_id,
            )
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()