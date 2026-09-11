from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from backend.models.task import Task
from backend.models.user import User, UserRole
from backend.repositories.class_repository import ClassRepository
from backend.repositories.course_repository import CourseRepository
from backend.repositories.enrollment_repository import EnrollmentRepository
from backend.repositories.task_repository import TaskRepository
from backend.schemas.task.task_response import ClassInfo, TaskResponse
from sqlalchemy.ext.asyncio import AsyncSession


class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.task_repo = TaskRepository(db)
        self.course_repo = CourseRepository(db)
        self.class_repo = ClassRepository(db)
        self.enroll_repo = EnrollmentRepository(db)

    async def _get_enrolled_class(
        self,
        student_id: UUID,
        course_id: UUID,
    ):
        classes = await self.class_repo.get_by_course(course_id=course_id)
        for cls in classes:
            enrollment = await self.enroll_repo.find(
                student_id=student_id,
                class_id=cls.id,
            )
            if enrollment:
                return cls
        return None

    # Called before returning tasks to any user. Teacher can re-activate
    # manually via update_task.
    async def _auto_deactivate_overdue(self, tasks: List[Task]) -> List[Task]:
        """
        Jika task masih aktif tapi due_date sudah lewat,
        otomatis set is_active=False di DB dan return task yang sudah diupdate.
        """
        now = datetime.now(timezone.utc)
        result = []
        for task in tasks:
            if (
                task.is_active
                and task.due_date is not None
                and task.due_date < now
            ):
                task = await self.task_repo.update(task, {"is_active": False})
            result.append(task)
        return result

    async def _build_response(
        self,
        task: Task,
        class_id: Optional[UUID] = None,
    ) -> TaskResponse:
        class_info = None
        if class_id:
            cls = await self.class_repo.get(class_id)
            if cls:
                class_info = ClassInfo(id=cls.id, name=cls.name)

        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            due_date=task.due_date,
            is_active=task.is_active,
            course_id=task.course_id,   
            class_id=class_id,
            class_info=class_info,
        )

    async def create_task(
        self,
        current_user: User,
        course_id: UUID,
        data: dict,
    ) -> Task:

        if current_user.role != UserRole.TEACHER:
            raise PermissionError("Only teachers can create tasks.")

        course = await self.course_repo.get(course_id)
        if not course:
            raise ValueError("Course not found.")

        if course.teacher_id != current_user.id:
            raise PermissionError("You do not own this course.")

        data["course_id"] = course_id
        return await self.task_repo.create(Task(**data))

    async def get_tasks_by_course(
        self,
        current_user: User,
        course_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[TaskResponse]:

        course = await self.course_repo.get(course_id)
        if not course:
            raise ValueError("Course not found.")

        if current_user.role == UserRole.TEACHER:
            if course.teacher_id != current_user.id:
                raise PermissionError("Access denied.")

            tasks = await self.task_repo.get_by_course(course_id, skip, limit)
            # For teacher, find first class of course for display
            classes = await self.class_repo.get_by_course(course_id=course_id)
            class_id = classes[0].id if classes else None
            return [await self._build_response(t, class_id) for t in tasks]

        # Student: find enrolled class
        enrolled_cls = await self._get_enrolled_class(current_user.id, course.id)
        if not enrolled_cls:
            raise PermissionError("You are not enrolled in this course.")

        tasks = await self.task_repo.get_by_course(course_id, skip, limit)
        return [await self._build_response(t, enrolled_cls.id) for t in tasks]

    async def get_tasks_by_class(
        self,
        current_user: User,
        class_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[TaskResponse]:

        cls = await self.class_repo.get(class_id)
        if not cls:
            raise ValueError("Class not found.")

        course = await self.course_repo.get(cls.course_id)
        if not course:
            raise ValueError("Course not found.")

        if current_user.role == UserRole.TEACHER:
            if course.teacher_id != current_user.id:
                raise PermissionError("Access denied.")

            tasks = await self.task_repo.get_by_course(course.id, skip, limit)
            return [await self._build_response(t, class_id) for t in tasks]

        # Student
        enrollment = await self.enroll_repo.find(
            student_id=current_user.id,
            class_id=class_id,
        )
        if not enrollment:
            raise PermissionError("You are not enrolled in this class.")

        tasks = await self.task_repo.get_by_course(course.id, skip, limit)
        return [await self._build_response(t, class_id) for t in tasks]

    async def get_task_detail(
        self,
        current_user: User,
        task_id: UUID,
    ) -> TaskResponse:

        task = await self.task_repo.get(task_id)
        if not task:
            raise ValueError("Task not found.")

        course = await self.course_repo.get(task.course_id)

        if current_user.role == UserRole.TEACHER:
            if course.teacher_id != current_user.id:
                raise PermissionError("Access denied.")

            classes = await self.class_repo.get_by_course(course_id=course.id)
            class_id = classes[0].id if classes else None
            return await self._build_response(task, class_id)

        # Student: find enrolled class for this course
        enrolled_cls = await self._get_enrolled_class(current_user.id, course.id)
        if not enrolled_cls:
            raise PermissionError("Access denied.")

        return await self._build_response(task, enrolled_cls.id)

    async def update_task(
        self,
        current_user: User,
        task_id: UUID,
        data: dict,
    ) -> Task:

        task = await self.task_repo.get(task_id)
        if not task:
            raise ValueError("Task not found.")

        course = await self.course_repo.get(task.course_id)
        if course.teacher_id != current_user.id:
            raise PermissionError("You do not own this task.")

        return await self.task_repo.update(task, data)

    async def delete_task(
        self,
        current_user: User,
        task_id: UUID,
    ):

        task = await self.task_repo.get(task_id)
        if not task:
            raise ValueError("Task not found.")

        course = await self.course_repo.get(task.course_id)
        if course.teacher_id != current_user.id:
            raise PermissionError("You do not own this task.")

        return await self.task_repo.delete(task_id)