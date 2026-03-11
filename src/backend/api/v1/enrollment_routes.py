from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.backend.api.deps import get_db, require_student, require_teacher
from src.backend.services.enrollment_service import EnrollmentService
from src.backend.schemas.enrollment.enrollment_create import EnrollmentCreate
from src.backend.schemas.enrollment.enrollment_response import EnrollmentResponse

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])


# ==============================
# STUDENT ENROLL
# ==============================
@router.post(
    "/",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED
)
async def enroll_in_class(
    data: EnrollmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_student)
):
    service = EnrollmentService(db)

    try:
        return await service.enroll_student(
            student=current_user,
            class_id=data.class_id
        )

    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        if "already enrolled" in str(e).lower():
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))


# ==============================
# STUDENT VIEW OWN ENROLLMENTS
# ==============================
@router.get(
    "/me",
    response_model=List[EnrollmentResponse]
)
async def get_my_enrollments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_student)
):
    service = EnrollmentService(db)

    try:
        return await service.get_student_enrollments(
            student=current_user,
            skip=skip,
            limit=limit
        )

    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# ==============================
# TEACHER VIEW CLASS ENROLLMENTS
# ==============================
@router.get(
    "/class/{class_id}",
    response_model=List[EnrollmentResponse]
)
async def get_class_enrollments(
    class_id,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_teacher)
):
    service = EnrollmentService(db)

    try:
        return await service.get_class_enrollments(
            current_user=current_user,
            class_id=class_id,
            skip=skip,
            limit=limit
        )

    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))