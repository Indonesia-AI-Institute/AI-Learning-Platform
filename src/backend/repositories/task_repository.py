from uuid import UUID
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.models.task import Task
from src.backend.repositories.base_repository import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, db: AsyncSession):
        super().__init__(Task, db)

    async def get_by_course(
        self,
        course_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:

        stmt = (
            select(Task)
            .where(Task.course_id == course_id)
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()