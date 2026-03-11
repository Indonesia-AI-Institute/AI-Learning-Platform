from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.api.deps import get_db, get_current_user, require_teacher
from src.backend.services.course_service import CourseService

from src.backend.schemas.course.course_create import CourseCreate
from src.backend.schemas.course.course_response import CourseResponse
from src.backend.schemas.course.course_update import CourseUpdate 

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.post("/create/", response_model=CourseResponse)
async def create_course(
    data: CourseCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_teacher)
):
    service = CourseService(db)

    try:
        course = await service.create_course(
            current_user=current_user,
            data=data.dict()
        )
        return course
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# @router.get("/{class_id}")
# async def get_courses(
#     class_id: UUID,
#     skip: int = 0,
#     limit: int = 100,
#     db: AsyncSession = Depends(get_db),
#     current_user = Depends(get_current_user)
# ):
#     service = CourseService(db)

#     try:
#         return await service.get_courses_by_class(
#             current_user=current_user,
#             class_id=class_id,
#             skip=skip,
#             limit=limit
#         )
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[CourseResponse])
async def get_my_courses(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = CourseService(db)
    return await service.get_my_courses(current_user, skip, limit)


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course_detail(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = CourseService(db)

    try:
        return await service.get_course_detail(
            current_user=current_user,
            course_id=course_id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: UUID,
    data: CourseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_teacher)
):
    service = CourseService(db)

    try:
        return await service.update_course(
            current_user=current_user,
            course_id=course_id,
            data=data.dict(exclude_unset=True)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{course_id}")
async def delete_course(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_teacher)
):
    service = CourseService(db)

    try:
        await service.delete_course(
            current_user=current_user,
            course_id=course_id
        )
        return {"detail": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))