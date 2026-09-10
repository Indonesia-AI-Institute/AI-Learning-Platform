from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.chat_session import ChatSession
from backend.models.task import Task
from backend.models.course import Course
from backend.repositories.base_repository import BaseRepository


class SessionRepository(BaseRepository[ChatSession]):
    def __init__(self, db: AsyncSession):
        super().__init__(ChatSession, db)

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

    # Used for listing sessions on the task detail page
    async def get_by_student_and_task(
        self,
        student_id: UUID,
        task_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ChatSession]:

        stmt = (
            select(ChatSession)
            .where(
                ChatSession.student_id == student_id,
                ChatSession.task_id == task_id,
            )
            .order_by(ChatSession.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    # Teacher is on Course, not Class
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