from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.models.enrollment import Enrollment
from src.backend.repositories.base_repository import BaseRepository


class EnrollmentRepository(BaseRepository[Enrollment]):
    def __init__(self, db: AsyncSession):
        super().__init__(Enrollment, db)

    async def get_by_student(
        self,
        student_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Enrollment]:

        stmt = (
            select(Enrollment)
            .where(Enrollment.student_id == student_id)
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_class(
        self,
        class_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Enrollment]:

        stmt = (
            select(Enrollment)
            .where(Enrollment.class_id == class_id)
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def find(
        self,
        student_id: UUID,
        class_id: UUID
    ) -> Enrollment | None:

        stmt = select(Enrollment).where(
            (Enrollment.student_id == student_id) &
            (Enrollment.class_id == class_id)
        )

        result = await self.db.execute(stmt)
        return result.scalars().first()