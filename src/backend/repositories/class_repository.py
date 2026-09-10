from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.models.course import Course
from backend.models.class_model import Class
from backend.repositories.base_repository import BaseRepository


class ClassRepository(BaseRepository[Class]):
    def __init__(self, db: AsyncSession):
        super().__init__(Class, db)

    async def get(self, class_id: UUID) -> Class | None:
        stmt = (
            select(Class)
            .options(selectinload(Class.course))
            .where(Class.id == class_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_and_teacher(
        self,
        class_id: UUID,
        teacher_id: UUID
    ) -> Class | None:
        stmt = (
            select(Class)
            .options(selectinload(Class.course))
            .join(Course)
            .where(
                Class.id == class_id,
                Course.teacher_id == teacher_id
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_course(
        self,
        course_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Class]:
        stmt = (
            select(Class)
            .options(selectinload(Class.course))
            .where(Class.course_id == course_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_teacher(
        self,
        teacher_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Class]:
        stmt = (
            select(Class)
            .options(selectinload(Class.course))
            .join(Course)
            .where(Course.teacher_id == teacher_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_ids(
        self,
        class_ids: List[UUID],
        skip: int = 0,
        limit: int = 100
    ) -> List[Class]:
        if not class_ids:
            return []
        stmt = (
            select(Class)
            .options(selectinload(Class.course))
            .where(Class.id.in_(class_ids))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()