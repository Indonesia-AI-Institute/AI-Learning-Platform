"""
analytics_routes.py
===================
"""

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.api.deps import get_db, get_current_user
from src.backend.utils.role_guard import RoleGuard
from src.backend.models.user import User, UserRole
from src.backend.services.session_analytics_service import SessionAnalyticsService
from src.backend.services.session_service import SessionService
from src.backend.services.prompt_classification_service import PromptClassificationService
from src.backend.schemas.analytics.analytics_response import AnalyticsResponse


router = APIRouter(prefix="/analytics", tags=["Analytics"])


# =========================================================
# STUDENT — MY ANALYTICS
# =========================================================

@router.get("/me", response_model=AnalyticsResponse)
async def get_my_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SessionAnalyticsService(db)
    analytics = await service.get_user_analytics(user_id=current_user.id)
    return AnalyticsResponse(**analytics)


# =========================================================
# STUDENT — MY PROMPT CLASSIFICATION
# =========================================================

@router.get("/me/classifications")
async def get_my_classifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Student: view own prompt type distribution.
    No student_id exposed — only own data.
    """
    service = PromptClassificationService(db)
    result = await service.get_my_classification(student_id=current_user.id)

    if not result:
        return {"message": "No classification data yet.", "data": None}

    return {"data": result}


# =========================================================
# TEACHER — CLASS ANALYTICS
# =========================================================

@router.get("/class/{class_id}")
async def get_class_analytics(
    class_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleGuard([UserRole.TEACHER])),
):
    service = SessionAnalyticsService(db)
    try:
        analytics = await service.get_class_analytics(class_id=class_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"class_id": str(class_id), "students": analytics}


# =========================================================
# TEACHER — CLASS PROMPT CLASSIFICATION
# =========================================================

@router.get("/class/{class_id}/classifications")
async def get_class_classifications(
    class_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleGuard([UserRole.TEACHER])),
):
    """
    Teacher: prompt type distribution per student in a class.
    """
    service = PromptClassificationService(db)
    try:
        result = await service.get_by_class(class_id=class_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"class_id": str(class_id), "students": result}


# =========================================================
# TEACHER — COURSE PROMPT CLASSIFICATION
# =========================================================

@router.get("/course/{course_id}/classifications")
async def get_course_classifications(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleGuard([UserRole.TEACHER])),
):
    """
    Teacher: prompt type distribution per student in a course.
    """
    service = PromptClassificationService(db)
    try:
        result = await service.get_by_course(course_id=course_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"course_id": str(course_id), "students": result}


# =========================================================
# TEACHER — TASK ANALYTICS
# =========================================================

@router.get("/task/{task_id}")
async def get_task_analytics(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleGuard([UserRole.TEACHER])),
):
    service = SessionAnalyticsService(db)
    try:
        analytics = await service.get_task_analytics(task_id=task_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"task_id": str(task_id), "students": analytics}


# =========================================================
# TEACHER — TASK PROMPT CLASSIFICATION
# =========================================================

@router.get("/task/{task_id}/classifications")
async def get_task_classifications(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleGuard([UserRole.TEACHER])),
):
    """
    Teacher: prompt type distribution per student for a specific task.
    """
    service = PromptClassificationService(db)
    try:
        result = await service.get_by_task(task_id=task_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"task_id": str(task_id), "students": result}


# =========================================================
# TEACHER — STUDENT PROMPT CLASSIFICATION
# =========================================================

@router.get("/student/{student_id}/classifications")
async def get_student_classifications(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleGuard([UserRole.TEACHER])),
):
    """
    Teacher: prompt type distribution for a specific student.
    """
    service = PromptClassificationService(db)
    try:
        result = await service.get_by_student(student_id=student_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"student_id": str(student_id), "data": result}


# =========================================================
# TEACHER — SESSION DETAIL ANALYTICS
# =========================================================

@router.get("/sessions/{session_id}")
async def get_session_analytics(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleGuard([UserRole.TEACHER])),
):
    analytics_service = SessionAnalyticsService(db)
    session_service = SessionService(db)

    try:
        await session_service.get_session_detail(
            current_user=current_user,
            session_id=session_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    analytics = await analytics_service.get_session_analytics(session_id=session_id)

    if not analytics:
        raise HTTPException(
            status_code=404,
            detail="Analytics not found. Session may not have been ended yet.",
        )

    return analytics