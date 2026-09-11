from uuid import UUID

from backend.api.deps import get_current_user, get_db, require_teacher
from backend.schemas.course.course_create import CourseCreate
from backend.schemas.course.course_response import CourseResponse
from backend.schemas.course.course_update import CourseUpdate
from backend.services.course_service import CourseService
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.post("/create/", response_model=CourseResponse)
async def create_course(
    data: CourseCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_teacher),
):
    service = CourseService(db)
    try:
        return await service.create_course(current_user=current_user, data=data.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# MUST be before /{course_id} to avoid route conflict.
@router.get("/all", response_model=list[CourseResponse])
async def get_all_courses(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = CourseService(db)
    return await service.get_all_active_courses(skip=skip, limit=limit)


@router.get("/", response_model=list[CourseResponse])
async def get_my_courses(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = CourseService(db)
    return await service.get_my_courses(current_user, skip, limit)


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course_detail(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = CourseService(db)
    try:
        return await service.get_course_detail(
            current_user=current_user, course_id=course_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: UUID,
    data: CourseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_teacher),
):
    service = CourseService(db)
    try:
        return await service.update_course(
            current_user=current_user,
            course_id=course_id,
            data=data.dict(exclude_unset=True),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{course_id}")
async def delete_course(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_teacher),
):
    service = CourseService(db)
    try:
        await service.delete_course(
            current_user=current_user, course_id=course_id
        )
        return {"detail": "deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))