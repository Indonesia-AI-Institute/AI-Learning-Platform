"""
analytics_routes.py
===================
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.api.deps import get_db, get_current_user
from src.backend.utils.role_guard import RoleGuard
from src.backend.models.user import User, UserRole
from src.backend.services.session_analytics_service import SessionAnalyticsService
from src.backend.services.session_service import SessionService
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
    """
    Student: get aggregated analytics across all own sessions.
    """
    service = SessionAnalyticsService(db)
    analytics = await service.get_user_analytics(user_id=current_user.id)
    return AnalyticsResponse(**analytics)


# =========================================================
# TEACHER — CLASS ANALYTICS
# =========================================================

@router.get("/class/{class_id}")
async def get_class_analytics(
    class_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleGuard([UserRole.TEACHER])),
):
    """
    Teacher: get per-student analytics summary for all students in a class.
    """
    service = SessionAnalyticsService(db)

    try:
        analytics = await service.get_class_analytics(class_id=class_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"class_id": str(class_id), "students": analytics}


# =========================================================
# TEACHER — TASK ANALYTICS
# =========================================================

@router.get("/task/{task_id}")
async def get_task_analytics(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleGuard([UserRole.TEACHER])),
):
    """
    Teacher: get per-student analytics for a specific task.
    Compare how different students approached the same task.
    """
    service = SessionAnalyticsService(db)

    try:
        analytics = await service.get_task_analytics(task_id=task_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"task_id": str(task_id), "students": analytics}


# =========================================================
# TEACHER — SESSION DETAIL ANALYTICS
# =========================================================

@router.get("/sessions/{session_id}")
async def get_session_analytics(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleGuard([UserRole.TEACHER])),
):
    """
    Teacher: get detailed analytics for a single session.
    """
    analytics_service = SessionAnalyticsService(db)
    session_service = SessionService(db)

    # Validate teacher has access to this session
    try:
        await session_service.get_session_detail(
            current_user=current_user,
            session_id=session_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    analytics = await analytics_service.get_session_analytics(
        session_id=session_id
    )

    if not analytics:
        raise HTTPException(
            status_code=404,
            detail="Analytics not found. Session may not have been ended yet.",
        )

    return analytics