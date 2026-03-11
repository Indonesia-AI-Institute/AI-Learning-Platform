from typing import Type, TypeVar, Generic, Optional, List, Any, Dict
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.models.base import BaseModel


ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """
    Async generic base repository for CRUD operations.
    """

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    # =========================
    # CREATE
    # =========================

    async def create(self, obj: ModelType) -> ModelType:
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    # =========================
    # GET BY ID
    # =========================

    async def get(self, obj_id: UUID) -> Optional[ModelType]:
        stmt = select(self.model).where(self.model.id == obj_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # =========================
    # GET ALL
    # =========================

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ModelType]:

        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    # =========================
    # UPDATE
    # =========================

    async def update(
        self,
        db_obj: ModelType,
        obj_in: Dict[str, Any],
    ) -> ModelType:

        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    # =========================
    # HARD DELETE
    # =========================

    async def delete(self, obj_id: UUID) -> Optional[ModelType]:
        db_obj = await self.get(obj_id)
        if not db_obj:
            return None

        await self.db.delete(db_obj)
        await self.db.commit()
        return db_obj

    # =========================
    # SOFT DELETE
    # =========================

    async def soft_delete(self, obj_id: UUID) -> Optional[ModelType]:
        db_obj = await self.get(obj_id)
        if not db_obj:
            return None

        if hasattr(db_obj, "soft_delete"):
            db_obj.soft_delete()
            self.db.add(db_obj)
            await self.db.commit()
            await self.db.refresh(db_obj)
            return db_obj

        raise AttributeError(
            f"{self.model.__name__} does not support soft delete"
        )

    # =========================
    # FILTER BY FIELD
    # =========================

    async def filter_by(self, **filters: Any) -> List[ModelType]:

        stmt = select(self.model)

        for field, value in filters.items():
            if hasattr(self.model, field):
                stmt = stmt.where(getattr(self.model, field) == value)

        result = await self.db.execute(stmt)
        return result.scalars().all()