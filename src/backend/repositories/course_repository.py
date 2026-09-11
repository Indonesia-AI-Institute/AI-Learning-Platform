from typing import List, Optional
from uuid import UUID

from backend.models.course import Course
from backend.repositories.base_repository import BaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class CourseRepository(BaseRepository[Course]):
    def __init__(self, db: AsyncSession):
        super().__init__(Course, db)

    # Override get to eager load teacher
    async def get(self, obj_id: UUID) -> Optional[Course]:
        stmt = (
            select(Course)
            .options(selectinload(Course.teacher))
            .where(Course.id == obj_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_teacher(
        self,
        teacher_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Course]:
        stmt = (
            select(Course)
            .options(selectinload(Course.teacher))
            .where(Course.teacher_id == teacher_id)
            .order_by(Course.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_all_active(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Course]:
        stmt = (
            select(Course)
            .options(selectinload(Course.teacher))
            .where(Course.is_active.is_(True))
            .order_by(Course.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_ids(
        self,
        course_ids: List[UUID],
        skip: int = 0,
        limit: int = 100,
    ) -> List[Course]:
        if not course_ids:
            return []
        stmt = (
            select(Course)
            .options(selectinload(Course.teacher))
            .where(Course.id.in_(course_ids))
            .order_by(Course.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()