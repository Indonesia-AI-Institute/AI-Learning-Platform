from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.api.deps import get_db, require_teacher, get_current_user
from src.backend.services.class_service import ClassService

from src.backend.schemas.classes.class_create import ClassCreate
from src.backend.schemas.classes.class_update import ClassUpdate
from src.backend.schemas.classes.class_response import ClassResponse

router = APIRouter(prefix="/classes", tags=["Classes"])


@router.post("/", response_model=ClassResponse)
async def create_class(
    data: ClassCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_teacher)
):
    service = ClassService(db)
    return await service.create_class(current_user, data.dict())


@router.get("/", response_model=list[ClassResponse])
async def get_my_classes(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = ClassService(db)
    return await service.get_my_classes(current_user, skip, limit)


@router.get("/{class_id}", response_model=ClassResponse)
async def get_class_detail(
    class_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = ClassService(db)
    return await service.get_class_detail(current_user, class_id)


@router.put("/{class_id}", response_model=ClassResponse)
async def update_class(
    class_id: UUID,
    data: ClassUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_teacher)
):
    service = ClassService(db)
    return await service.update_class(
        current_user,
        class_id,
        data.model_dump(exclude_unset=True)
    )


@router.delete("/{class_id}")
async def delete_class(
    class_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_teacher)
):
    service = ClassService(db)
    await service.delete_class(current_user, class_id)
    return {"detail": "deleted"}