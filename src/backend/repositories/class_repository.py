from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.backend.models.course import Course
from src.backend.models.class_model import Class
from src.backend.repositories.base_repository import BaseRepository


class ClassRepository(BaseRepository[Class]):
    def __init__(self, db: AsyncSession):
        super().__init__(Class, db)

    # =========================
    # GET CLASS BY ID (EAGER LOAD COURSE)
    # =========================
    async def get(self, class_id: UUID) -> Class | None:
        stmt = (
            select(Class)
            .options(selectinload(Class.course))  # penting untuk async
            .where(Class.id == class_id)
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # =========================
    # GET CLASS BY ID + OWNERSHIP CHECK (RECOMMENDED)
    # =========================
    async def get_by_id_and_teacher(
        self,
        class_id: UUID,
        teacher_id: UUID
    ) -> Class | None:

        stmt = (
            select(Class)
            .join(Course)
            .where(
                Class.id == class_id,
                Course.teacher_id == teacher_id
            )
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


    # =========================
    # GET CLASSES BY COURSE
    # =========================
    async def get_by_course(
        self,
        course_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Class]:

        stmt = (
            select(Class)
            .where(Class.course_id == course_id)
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    # =========================
    # GET CLASSES BY TEACHER (via join)
    # =========================
    async def get_by_teacher(
        self,
        teacher_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Class]:

        stmt = (
            select(Class)
            .join(Course)
            .where(Course.teacher_id == teacher_id)
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    # =========================
    # GET CLASSES BY IDS
    # =========================
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
            .where(Class.id.in_(class_ids))
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    # =========================
    # GET CLASS BY COURSE ID
    # =========================
    async def get_by_course_id(self, course_id):
        result = await self.db.execute(
            select(Class).where(Class.course_id == course_id)
        )
        return result.scalar_one_or_none()