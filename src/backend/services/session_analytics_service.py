"""
Analytics for chat sessions. Analytics are finalized when a session is ended.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.models.session_analytics import SessionAnalytics
from backend.models.chat_session import ChatSession
from backend.models.chat_history import ChatHistory, MessageRole
from backend.models.task import Task
from backend.models.course import Course
from backend.models.class_model import Class


class SessionAnalyticsService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def finalize_session_analytics(
        self,
        session: ChatSession,
    ) -> SessionAnalytics:
        """
        Aggregate all metrics from ChatHistory and persist to SessionAnalytics.
        Called when student ends a session.
        """

        session_id = session.id

        # --- Total prompts & avg prompt length (user messages only) ---
        user_messages_stmt = (
            select(ChatHistory.content)
            .where(
                ChatHistory.session_id == session_id,
                ChatHistory.role == MessageRole.USER,
            )
        )
        result = await self.db.execute(user_messages_stmt)
        user_messages = result.scalars().all()

        total_prompts = len(user_messages)
        avg_prompt_length = (
            sum(len(m) for m in user_messages) / total_prompts
            if total_prompts > 0
            else 0.0
        )

        # --- Session duration (first message to last message) ---
        duration_stmt = (
            select(
                func.min(ChatHistory.created_at),
                func.max(ChatHistory.created_at),
            )
            .where(ChatHistory.session_id == session_id)
        )
        duration_result = await self.db.execute(duration_stmt)
        first_msg, last_msg = duration_result.one()

        session_duration_seconds = 0
        if first_msg and last_msg and first_msg != last_msg:
            session_duration_seconds = int(
                (last_msg - first_msg).total_seconds()
            )

        # --- Token usage (from assistant messages) ---
        token_stmt = (
            select(
                func.coalesce(func.sum(ChatHistory.input_tokens), 0),
                func.coalesce(func.sum(ChatHistory.output_tokens), 0),
            )
            .where(
                ChatHistory.session_id == session_id,
                ChatHistory.role == MessageRole.ASSISTANT,
            )
        )
        token_result = await self.db.execute(token_stmt)
        total_prompt_tokens, total_completion_tokens = token_result.one()
        total_tokens = total_prompt_tokens + total_completion_tokens

        # --- Finish reason (from last assistant message) ---
        finish_reason_stmt = (
            select(ChatHistory.message_metadata)
            .where(
                ChatHistory.session_id == session_id,
                ChatHistory.role == MessageRole.ASSISTANT,
            )
            .order_by(ChatHistory.message_index.desc())
            .limit(1)
        )
        finish_result = await self.db.execute(finish_reason_stmt)
        last_metadata = finish_result.scalar_one_or_none()
        finish_reason = (
            last_metadata.get("finish_reason") if last_metadata else None
        )

        # --- Upsert analytics (handle resume: update existing record) ---
        existing_stmt = select(SessionAnalytics).where(
            SessionAnalytics.chat_session_id == session_id
        )
        existing_result = await self.db.execute(existing_stmt)
        analytics = existing_result.scalar_one_or_none()

        if analytics:
            # Session was resumed — update existing record
            analytics.total_prompts = total_prompts
            analytics.avg_prompt_length = round(avg_prompt_length, 2)
            analytics.session_duration_seconds = session_duration_seconds
            analytics.prompt_tokens = total_prompt_tokens
            analytics.completion_tokens = total_completion_tokens
            analytics.total_tokens = total_tokens
            analytics.finish_reason = finish_reason
        else:
            # First time ending this session
            analytics = SessionAnalytics(
                chat_session_id=session_id,
                user_id=session.student_id,
                task_id=session.task_id,
                total_prompts=total_prompts,
                avg_prompt_length=round(avg_prompt_length, 2),
                session_duration_seconds=session_duration_seconds,
                prompt_tokens=total_prompt_tokens,
                completion_tokens=total_completion_tokens,
                total_tokens=total_tokens,
                finish_reason=finish_reason,
            )
            self.db.add(analytics)

        await self.db.commit()
        await self.db.refresh(analytics)

        return analytics

    async def get_user_analytics(self, user_id: UUID) -> dict:
        """
        Aggregated analytics for a single student across all sessions.
        """

        stmt = (
            select(
                func.count(SessionAnalytics.id),
                func.coalesce(func.sum(SessionAnalytics.total_prompts), 0),
                func.coalesce(func.sum(SessionAnalytics.prompt_tokens), 0),
                func.coalesce(func.sum(SessionAnalytics.completion_tokens), 0),
                func.coalesce(func.sum(SessionAnalytics.total_tokens), 0),
                func.coalesce(func.avg(SessionAnalytics.avg_prompt_length), 0.0),
                func.coalesce(func.sum(SessionAnalytics.session_duration_seconds), 0),
                func.max(SessionAnalytics.created_at),
            )
            .where(SessionAnalytics.user_id == user_id)
        )

        result = await self.db.execute(stmt)
        (
            total_sessions,
            total_prompts,
            total_prompt_tokens,
            total_completion_tokens,
            total_tokens,
            avg_prompt_length,
            total_duration_seconds,
            last_active,
        ) = result.one()

        return {
            "total_sessions": total_sessions or 0,
            "total_prompts": total_prompts or 0,
            "total_prompt_tokens": total_prompt_tokens or 0,
            "total_completion_tokens": total_completion_tokens or 0,
            "total_tokens": total_tokens or 0,
            "avg_prompt_length": round(float(avg_prompt_length or 0), 2),
            "total_duration_seconds": total_duration_seconds or 0,
            "last_active": last_active,
        }

    async def get_class_analytics(self, class_id: UUID, teacher_id: UUID) -> list[dict]:
        """
        Per-student analytics summary for all students in a class.
        Teacher uses this to compare prompting behavior across students.

        Scoped to `teacher_id` — a class outside the caller's own courses
        yields an empty result rather than another teacher's data.
        """

        stmt = (
            select(
                SessionAnalytics.user_id,
                func.count(SessionAnalytics.id),
                func.coalesce(func.sum(SessionAnalytics.total_prompts), 0),
                func.coalesce(func.sum(SessionAnalytics.total_tokens), 0),
                func.coalesce(func.avg(SessionAnalytics.avg_prompt_length), 0.0),
                func.coalesce(func.sum(SessionAnalytics.session_duration_seconds), 0),
                func.max(SessionAnalytics.created_at),
            )
            .join(ChatSession, SessionAnalytics.chat_session_id == ChatSession.id)
            .join(Task, SessionAnalytics.task_id == Task.id)
            .join(Course, Task.course_id == Course.id)
            .join(Class, Course.id == Class.course_id)
            .where(Class.id == class_id, Course.teacher_id == teacher_id)
            .group_by(SessionAnalytics.user_id)
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        return [
            {
                "student_id": str(row[0]),
                "total_sessions": row[1],
                "total_prompts": row[2],
                "total_tokens": row[3],
                "avg_prompt_length": round(float(row[4] or 0), 2),
                "total_duration_seconds": row[5],
                "last_active": row[6],
            }
            for row in rows
        ]

    async def get_task_analytics(self, task_id: UUID, teacher_id: UUID) -> list[dict]:
        """
        Per-student analytics for a specific task.
        Teacher uses this to compare how students approached the same task.

        Scoped to `teacher_id` — a task outside the caller's own courses
        yields an empty result rather than another teacher's data.
        """

        stmt = (
            select(
                SessionAnalytics.user_id,
                func.count(SessionAnalytics.id),
                func.coalesce(func.sum(SessionAnalytics.total_prompts), 0),
                func.coalesce(func.sum(SessionAnalytics.total_tokens), 0),
                func.coalesce(func.avg(SessionAnalytics.avg_prompt_length), 0.0),
                func.coalesce(func.sum(SessionAnalytics.session_duration_seconds), 0),
                func.max(SessionAnalytics.created_at),
            )
            .join(Task, SessionAnalytics.task_id == Task.id)
            .join(Course, Task.course_id == Course.id)
            .where(SessionAnalytics.task_id == task_id, Course.teacher_id == teacher_id)
            .group_by(SessionAnalytics.user_id)
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        return [
            {
                "student_id": str(row[0]),
                "total_sessions": row[1],
                "total_prompts": row[2],
                "total_tokens": row[3],
                "avg_prompt_length": round(float(row[4] or 0), 2),
                "total_duration_seconds": row[5],
                "last_active": row[6],
            }
            for row in rows
        ]

    async def get_session_analytics(self, session_id: UUID) -> dict | None:
        """
        Detailed analytics for a single session.
        """

        stmt = select(SessionAnalytics).where(
            SessionAnalytics.chat_session_id == session_id
        )

        result = await self.db.execute(stmt)
        analytics = result.scalar_one_or_none()

        if not analytics:
            return None

        return {
            "session_id": str(session_id),
            "student_id": str(analytics.user_id),
            "task_id": str(analytics.task_id),
            "total_prompts": analytics.total_prompts,
            "avg_prompt_length": analytics.avg_prompt_length,
            "session_duration_seconds": analytics.session_duration_seconds,
            "prompt_tokens": analytics.prompt_tokens,
            "completion_tokens": analytics.completion_tokens,
            "total_tokens": analytics.total_tokens,
            "finish_reason": analytics.finish_reason,
            "created_at": analytics.created_at,
            "updated_at": analytics.updated_at,
        }