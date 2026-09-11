from typing import List, Optional

from backend.models.user import User, UserRole
from backend.repositories.base_repository import BaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository(BaseRepository[User]):

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = (
            select(self.model)
            .where(
                self.model.email == email,
                self.model.is_deleted == False  # noqa: E712 — SQLAlchemy operator overload, not a Python bool check
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_role(
        self,
        role: UserRole,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:

        stmt = (
            select(self.model)
            .where(
                self.model.role == role,
                self.model.is_deleted == False  # noqa: E712 — SQLAlchemy operator overload, not a Python bool check
            )
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()