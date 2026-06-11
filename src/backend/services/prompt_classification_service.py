"""
services/prompt_classification_service.py
==========================================
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select, Integer
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import cast

from src.backend.models.prompt_classification import PromptClassification
from src.backend.models.chat_history import ChatHistory
from src.backend.models.chat_session import ChatSession
from src.backend.models.task import Task
from src.backend.models.course import Course
from src.backend.models.class_model import Class
from src.backend.models.user import User


def _pct(count: int, total: int) -> float:
    """Hitung persentase, aman dari division by zero."""
    if total == 0:
        return 0.0
    return round(count / total * 100, 1)


def _build_row(row) -> dict:
    """Convert raw SQL row → dict dengan persentase."""
    total = int(row.total_prompts) if row.total_prompts else 0
    return {
        "student_id": str(row.student_id),
        "student_name": row.student_name or "Unknown",
        "total_prompts": total,
        "direct_answer_pct": _pct(int(row.direct_answer or 0), total),
        "explanation_pct": _pct(int(row.explanation or 0), total),
        "step_by_step_pct": _pct(int(row.step_by_step or 0), total),
        "example_pct": _pct(int(row.example or 0), total),
        "rewrite_pct": _pct(int(row.rewrite or 0), total),
        "feedback_pct": _pct(int(row.feedback or 0), total),
        "summary_pct": _pct(int(row.summary or 0), total),
        "translation_pct": _pct(int(row.translation or 0), total),
        "brainstorm_pct": _pct(int(row.brainstorm or 0), total),
    }


def _classification_select():
    """Base SELECT columns — reused di semua query."""
    return select(
        ChatSession.student_id,
        User.full_name.label("student_name"),
        func.count(PromptClassification.id).label("total_prompts"),
        func.sum(cast(PromptClassification.is_direct_answer, Integer)).label("direct_answer"),
        func.sum(cast(PromptClassification.is_explanation, Integer)).label("explanation"),
        func.sum(cast(PromptClassification.is_step_by_step, Integer)).label("step_by_step"),
        func.sum(cast(PromptClassification.is_example, Integer)).label("example"),
        func.sum(cast(PromptClassification.is_rewrite, Integer)).label("rewrite"),
        func.sum(cast(PromptClassification.is_feedback, Integer)).label("feedback"),
        func.sum(cast(PromptClassification.is_summary, Integer)).label("summary"),
        func.sum(cast(PromptClassification.is_translation, Integer)).label("translation"),
        func.sum(cast(PromptClassification.is_brainstorm, Integer)).label("brainstorm"),
    )


def _base_joins(stmt):
    """JOIN chain yang dipakai semua query."""
    return (
        stmt
        .join(ChatHistory, PromptClassification.chat_history_id == ChatHistory.id)
        .join(ChatSession, ChatHistory.session_id == ChatSession.id)
        .join(User, ChatSession.student_id == User.id)
    )
class PromptClassificationService:

    def __init__(self, db: AsyncSession):
        self.db = db

    # =========================
    # SAVE CLASSIFICATION
    # =========================

    async def save_classification(
        self,
        chat_history_id: UUID,
        session_id: UUID,
        student_id: UUID,
        task_id: UUID,
        flags: dict,
    ) -> None:
        """Simpan hasil klasifikasi prompt."""
        # Cek duplikat — skip jika sudah ada
        existing = await self.db.execute(
            select(PromptClassification).where(
                PromptClassification.chat_history_id == chat_history_id
            )
        )
        if existing.scalar_one_or_none():
            return

        obj = PromptClassification(
            chat_history_id=chat_history_id,
            session_id=session_id,
            student_id=student_id,
            task_id=task_id,
            is_direct_answer=flags.get("is_direct_answer", False),
            is_explanation=flags.get("is_explanation", False),
            is_step_by_step=flags.get("is_step_by_step", False),
            is_example=flags.get("is_example", False),
            is_rewrite=flags.get("is_rewrite", False),
            is_feedback=flags.get("is_feedback", False),
            is_summary=flags.get("is_summary", False),
            is_translation=flags.get("is_translation", False),
            is_brainstorm=flags.get("is_brainstorm", False),
        )
        self.db.add(obj)
        await self.db.commit()

    # =========================
    # AGGREGATE QUERY HELPER
    # =========================

    # def _build_aggregate_select(self):
    #     """Build reusable aggregate select for classification stats."""
    #     return select(
    #         PromptClassification.student_id,
    #         func.count(PromptClassification.id).label("total_prompts"),
    #         func.coalesce(func.sum(PromptClassification.is_direct_answer.cast(Integer)), 0).label("direct_answer"),
    #         func.coalesce(func.sum(PromptClassification.is_explanation.cast(Integer)), 0).label("explanation"),
    #         func.coalesce(func.sum(PromptClassification.is_step_by_step.cast(Integer)), 0).label("step_by_step"),
    #         func.coalesce(func.sum(PromptClassification.is_example.cast(Integer)), 0).label("example"),
    #         func.coalesce(func.sum(PromptClassification.is_rewrite.cast(Integer)), 0).label("rewrite"),
    #         func.coalesce(func.sum(PromptClassification.is_feedback.cast(Integer)), 0).label("feedback"),
    #         func.coalesce(func.sum(PromptClassification.is_summary.cast(Integer)), 0).label("summary"),
    #         func.coalesce(func.sum(PromptClassification.is_translation.cast(Integer)), 0).label("translation"),
    #         func.coalesce(func.sum(PromptClassification.is_brainstorm.cast(Integer)), 0).label("brainstorm"),
    #     )

    # def _row_to_dict(self, row, include_student_id: bool = True) -> dict:
    #     total = row.total_prompts or 1

    #     result = {
    #         "total_prompts": row.total_prompts,
    #         "direct_answer_pct": round(row.direct_answer / total * 100, 1),
    #         "explanation_pct": round(row.explanation / total * 100, 1),
    #         "step_by_step_pct": round(row.step_by_step / total * 100, 1),
    #         "example_pct": round(row.example / total * 100, 1),
    #         "rewrite_pct": round(row.rewrite / total * 100, 1),
    #         "feedback_pct": round(row.feedback / total * 100, 1),
    #         "summary_pct": round(row.summary / total * 100, 1),
    #         "translation_pct": round(row.translation / total * 100, 1),
    #         "brainstorm_pct": round(row.brainstorm / total * 100, 1),
    #     }

    #     if include_student_id:
    #         result["student_id"] = str(row.student_id)

    #     return result

    # =========================
    # GET BY TASK
    # =========================

    async def get_classifications_by_task(self, task_id: UUID) -> List[dict]:
        stmt = (
            _base_joins(_classification_select())
            .where(ChatSession.task_id == task_id)
            .group_by(ChatSession.student_id, User.full_name)
            .order_by(User.full_name)
        )
        result = await self.db.execute(stmt)
        return [_build_row(row) for row in result.fetchall()]

    # =========================
    # GET BY CLASS
    # =========================

    async def get_classifications_by_class(self, class_id: UUID) -> List[dict]:
        stmt = (
            _base_joins(_classification_select())
            .join(Task, ChatSession.task_id == Task.id)
            .join(Class, Task.class_id == Class.id)
            .where(Class.id == class_id)
            .group_by(ChatSession.student_id, User.full_name)
            .order_by(User.full_name)
        )
        result = await self.db.execute(stmt)
        return [_build_row(row) for row in result.fetchall()]

    # =========================
    # GET BY COURSE
    # =========================

    async def get_classifications_by_course(self, course_id: UUID) -> List[dict]:
        stmt = (
            _base_joins(_classification_select())
            .join(Task, ChatSession.task_id == Task.id)
            .join(Course, Task.course_id == Course.id)
            .where(Course.id == course_id)
            .group_by(ChatSession.student_id, User.full_name)
            .order_by(User.full_name)
        )
        result = await self.db.execute(stmt)
        return [_build_row(row) for row in result.fetchall()]

    # =========================
    # GET BY STUDENT
    # =========================

    async def get_classifications_by_student(self, student_id: UUID) -> List[dict]:
        stmt = (
            _base_joins(_classification_select())
            .where(ChatSession.student_id == student_id)
            .group_by(ChatSession.student_id, User.full_name)
        )
        result = await self.db.execute(stmt)
        return [_build_row(row) for row in result.fetchall()]

    # =========================
    # GET MY OWN (student view)
    # =========================

    async def get_my_classifications(self, student_id: UUID) -> Optional[dict]:
        rows = await self.get_classifications_by_student(student_id)
        return rows[0] if rows else None