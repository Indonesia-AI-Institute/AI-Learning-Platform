from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.models.user import User, UserRole
from src.backend.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    # =========================
    # GET BY EMAIL
    # =========================

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = (
            select(self.model)
            .where(
                self.model.email == email,
                self.model.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # # =========================
    # # GET BY USERNAME
    # # =========================

    # async def get_by_username(self, username: str) -> Optional[User]:
    #     stmt = select(self.model).where(self.model.username == username)
    #     result = await self.db.execute(stmt)
    #     return result.scalar_one_or_none()

    # =========================
    # GET BY ROLE
    # =========================

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
                self.model.is_deleted == False
            )
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    # =========================
    # GET STUDENTS
    # =========================

    async def get_students(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        return await self.get_by_role(UserRole.STUDENT, skip, limit)

    # =========================
    # GET TEACHERS
    # =========================

    async def get_teachers(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        return await self.get_by_role(UserRole.TEACHER, skip, limit)