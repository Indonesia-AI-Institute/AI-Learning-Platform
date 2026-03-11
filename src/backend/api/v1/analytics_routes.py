"""
analytics_routes.py
===================
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.api.deps import get_db, get_current_user
from src.backend.models.user import User
from src.backend.services.session_analytics_service import SessionAnalyticsService
from src.backend.schemas.analytics.analytics_response import AnalyticsResponse


router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/me", response_model=AnalyticsResponse)
async def get_my_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SessionAnalyticsService(db)

    analytics = await service.get_user_analytics(
        user_id=current_user.id
    )

    return AnalyticsResponse(**analytics)