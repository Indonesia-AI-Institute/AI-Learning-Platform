from typing import List
from uuid import UUID

from backend.api.deps import get_current_user, get_db, require_teacher
from backend.schemas.classes.class_create import ClassCreate
from backend.schemas.classes.class_response import ClassResponse
from backend.schemas.classes.class_update import ClassUpdate
from backend.services.class_service import ClassService
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/classes", tags=["Classes"])


@router.post("/", response_model=ClassResponse)
async def create_class(
    data: ClassCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_teacher),
):
    service = ClassService(db)
    try:
        return await service.create_class(current_user, data.dict())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# For student: see classes in a course before enrolling.
# MUST be before /{class_id} to avoid route conflict.
@router.get("/course/{course_id}", response_model=List[ClassResponse])
async def get_classes_by_course(
    course_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ClassService(db)
    try:
        return await service.get_classes_by_course(
            course_id=course_id,
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[ClassResponse])
async def get_my_classes(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ClassService(db)
    try:
        return await service.get_my_classes(current_user, skip, limit)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/{class_id}", response_model=ClassResponse)
async def get_class_detail(
    class_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ClassService(db)
    try:
        return await service.get_class_detail(current_user, class_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.put("/{class_id}", response_model=ClassResponse)
async def update_class(
    class_id: UUID,
    data: ClassUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_teacher),
):
    service = ClassService(db)
    try:
        return await service.update_class(
            current_user, class_id, data.model_dump(exclude_unset=True)
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{class_id}")
async def delete_class(
    class_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_teacher),
):
    service = ClassService(db)
    try:
        await service.delete_class(current_user, class_id)
        return {"detail": "deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))