from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, Integer

from backend.models.prompt_classification import PromptClassification
from backend.models.task import Task
from backend.models.course import Course
from backend.models.class_model import Class
from backend.observability.logging.logger import get_logger

logger = get_logger(__name__)


class PromptClassificationService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_classification(
        self,
        chat_history_id: UUID,
        session_id: UUID,
        student_id: UUID,
        task_id: UUID,
        flags: dict,
    ) -> PromptClassification:

        classification = PromptClassification(
            chat_history_id=chat_history_id,
            session_id=session_id,
            student_id=student_id,
            task_id=task_id,
            is_direct_answer=flags.get("direct_answer", False),
            is_explanation=flags.get("explanation", False),
            is_step_by_step=flags.get("step_by_step", False),
            is_example=flags.get("example", False),
            is_rewrite=flags.get("rewrite", False),
            is_feedback=flags.get("feedback", False),
            is_summary=flags.get("summary", False),
            is_translation=flags.get("translation", False),
            is_brainstorm=flags.get("brainstorm", False),
        )

        self.db.add(classification)
        await self.db.commit()
        await self.db.refresh(classification)
        return classification

    def _build_aggregate_select(self):
        """Build reusable aggregate select for classification stats."""
        return select(
            PromptClassification.student_id,
            func.count(PromptClassification.id).label("total_prompts"),
            func.coalesce(func.sum(PromptClassification.is_direct_answer.cast(Integer)), 0).label("direct_answer"),
            func.coalesce(func.sum(PromptClassification.is_explanation.cast(Integer)), 0).label("explanation"),
            func.coalesce(func.sum(PromptClassification.is_step_by_step.cast(Integer)), 0).label("step_by_step"),
            func.coalesce(func.sum(PromptClassification.is_example.cast(Integer)), 0).label("example"),
            func.coalesce(func.sum(PromptClassification.is_rewrite.cast(Integer)), 0).label("rewrite"),
            func.coalesce(func.sum(PromptClassification.is_feedback.cast(Integer)), 0).label("feedback"),
            func.coalesce(func.sum(PromptClassification.is_summary.cast(Integer)), 0).label("summary"),
            func.coalesce(func.sum(PromptClassification.is_translation.cast(Integer)), 0).label("translation"),
            func.coalesce(func.sum(PromptClassification.is_brainstorm.cast(Integer)), 0).label("brainstorm"),
        )

    def _row_to_dict(self, row, include_student_id: bool = True) -> dict:
        total = row.total_prompts or 1

        result = {
            "total_prompts": row.total_prompts,
            "direct_answer_pct": round(row.direct_answer / total * 100, 1),
            "explanation_pct": round(row.explanation / total * 100, 1),
            "step_by_step_pct": round(row.step_by_step / total * 100, 1),
            "example_pct": round(row.example / total * 100, 1),
            "rewrite_pct": round(row.rewrite / total * 100, 1),
            "feedback_pct": round(row.feedback / total * 100, 1),
            "summary_pct": round(row.summary / total * 100, 1),
            "translation_pct": round(row.translation / total * 100, 1),
            "brainstorm_pct": round(row.brainstorm / total * 100, 1),
        }

        if include_student_id:
            result["student_id"] = str(row.student_id)

        return result

    async def get_by_task(self, task_id: UUID, teacher_id: UUID) -> list[dict]:
        """Scoped to `teacher_id` — a task outside the caller's own courses
        yields an empty result rather than another teacher's data."""
        stmt = (
            self._build_aggregate_select()
            .join(Task, PromptClassification.task_id == Task.id)
            .join(Course, Task.course_id == Course.id)
            .where(PromptClassification.task_id == task_id, Course.teacher_id == teacher_id)
            .group_by(PromptClassification.student_id)
        )
        result = await self.db.execute(stmt)
        return [self._row_to_dict(row) for row in result.all()]

    async def get_by_class(self, class_id: UUID, teacher_id: UUID) -> list[dict]:
        """Scoped to `teacher_id` — a class outside the caller's own courses
        yields an empty result rather than another teacher's data."""
        stmt = (
            self._build_aggregate_select()
            .join(Task, PromptClassification.task_id == Task.id)
            .join(Course, Task.course_id == Course.id)
            .join(Class, Course.id == Class.course_id)
            .where(Class.id == class_id, Course.teacher_id == teacher_id)
            .group_by(PromptClassification.student_id)
        )
        result = await self.db.execute(stmt)
        return [self._row_to_dict(row) for row in result.all()]

    async def get_by_course(self, course_id: UUID, teacher_id: UUID) -> list[dict]:
        """Scoped to `teacher_id` — a course the caller doesn't teach
        yields an empty result rather than another teacher's data."""
        stmt = (
            self._build_aggregate_select()
            .join(Task, PromptClassification.task_id == Task.id)
            .join(Course, Task.course_id == Course.id)
            .where(Task.course_id == course_id, Course.teacher_id == teacher_id)
            .group_by(PromptClassification.student_id)
        )
        result = await self.db.execute(stmt)
        return [self._row_to_dict(row) for row in result.all()]

    async def get_by_student(self, student_id: UUID, teacher_id: UUID) -> list[dict]:
        """Scoped to `teacher_id` — only classifications from tasks in the
        caller's own courses count, so a student the caller doesn't teach
        yields no data rather than another teacher's student data."""
        stmt = (
            self._build_aggregate_select()
            .join(Task, PromptClassification.task_id == Task.id)
            .join(Course, Task.course_id == Course.id)
            .where(
                PromptClassification.student_id == student_id,
                Course.teacher_id == teacher_id,
            )
            .group_by(PromptClassification.student_id)
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        if not rows:
            return []
        return [self._row_to_dict(rows[0])]

    async def get_my_classification(self, student_id: UUID) -> dict | None:
        stmt = (
            self._build_aggregate_select()
            .where(PromptClassification.student_id == student_id)
            .group_by(PromptClassification.student_id)
        )
        result = await self.db.execute(stmt)
        row = result.one_or_none()
        if not row:
            return None
        return self._row_to_dict(row, include_student_id=False)