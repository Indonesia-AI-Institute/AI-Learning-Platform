from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.backend.models.course import Course
from src.backend.repositories.base_repository import BaseRepository


class CourseRepository(BaseRepository[Course]):
    def __init__(self, db: AsyncSession):
        super().__init__(Course, db)

    # =========================
    # GET COURSES BY TEACHER
    # =========================

    async def get_by_teacher(
        self,
        teacher_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Course]:

        stmt = (
            select(Course)
            .where(Course.teacher_id == teacher_id)
            .order_by(Course.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    # =========================
    # GET ALL ACTIVE COURSES (Student browse)
    # =========================

    async def get_all_active(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Course]:

        stmt = (
            select(Course)
            .where(Course.is_active.is_(True))
            .order_by(Course.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    # =========================
    # GET COURSES BY IDS
    # =========================

    async def get_by_ids(
        self,
        course_ids: List[UUID],
        skip: int = 0,
        limit: int = 100
    ) -> List[Course]:

        if not course_ids:
            return []

        stmt = (
            select(Course)
            .where(Course.id.in_(course_ids))
            .order_by(Course.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    # =========================
    # GET DETAIL
    # =========================

    async def get_detail(
        self,
        course_id: UUID
    ) -> Optional[Course]:

        stmt = select(Course).where(Course.id == course_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()