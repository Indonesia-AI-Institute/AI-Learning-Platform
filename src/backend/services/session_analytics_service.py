"""
services/session_analytics_service.py
=====================================
Analytics for chat session usage.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.backend.models.session_analytics import SessionAnalytics
from src.backend.models.chat_session import ChatSession
from src.backend.models.chat_history import ChatHistory


class SessionAnalyticsService:

    def __init__(self, db: AsyncSession):
        self.db = db

    # =========================
    # CREATE ANALYTICS
    # =========================

    async def create_analytics(
        self,
        chat_session_id,
        user_id,
        usage: dict | None,
        finish_reason: str | None,
    ):
        analytics = SessionAnalytics(
            chat_session_id=chat_session_id,
            user_id=user_id,
            prompt_tokens=usage.get("prompt_tokens") if usage else None,
            completion_tokens=usage.get("completion_tokens") if usage else None,
            total_tokens=usage.get("total_tokens") if usage else None,
            finish_reason=finish_reason,
        )

        self.db.add(analytics)
        await self.db.commit()
        await self.db.refresh(analytics)

        return analytics

    # =====================================================
    # AGGREGATED ANALYTICS
    # =====================================================

    async def get_user_analytics(self, user_id):

        # total sessions (student)
        session_stmt = select(func.count()).select_from(ChatSession).where(
            ChatSession.student_id == user_id
        )
        total_sessions = await self.db.scalar(session_stmt)

        # total messages (join history -> session)
        message_stmt = (
            select(func.count())
            .select_from(ChatHistory)
            .join(ChatSession, ChatHistory.session_id == ChatSession.id)
            .where(ChatSession.student_id == user_id)
        )
        total_messages = await self.db.scalar(message_stmt)

        # token aggregation
        token_stmt = select(
            func.coalesce(func.sum(SessionAnalytics.prompt_tokens), 0),
            func.coalesce(func.sum(SessionAnalytics.completion_tokens), 0),
            func.coalesce(func.sum(SessionAnalytics.total_tokens), 0),
            func.max(SessionAnalytics.created_at),
        ).where(SessionAnalytics.user_id == user_id)

        result = await self.db.execute(token_stmt)
        (
            total_prompt_tokens,
            total_completion_tokens,
            total_tokens,
            last_active,
        ) = result.one()

        return {
            "total_sessions": total_sessions or 0,
            "total_messages": total_messages or 0,
            "total_prompt_tokens": total_prompt_tokens or 0,
            "total_completion_tokens": total_completion_tokens or 0,
            "total_tokens": total_tokens or 0,
            "last_active": last_active,
        }