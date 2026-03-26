from uuid import UUID
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.models.task import Task
from src.backend.models.user import User, UserRole

from src.backend.repositories.task_repository import TaskRepository
from src.backend.repositories.course_repository import CourseRepository
from src.backend.repositories.class_repository import ClassRepository
from src.backend.repositories.enrollment_repository import EnrollmentRepository


class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.task_repo = TaskRepository(db)
        self.course_repo = CourseRepository(db)
        self.class_repo = ClassRepository(db)
        self.enroll_repo = EnrollmentRepository(db)

    # =========================
    # CREATE TASK (Teacher Only)
    # =========================
    async def create_task(
        self,
        current_user: User,
        course_id: UUID,
        data: dict
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

    # =========================
    # GET TASKS BY COURSE
    # =========================
    async def get_tasks_by_course(
        self,
        current_user: User,
        course_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:

        course = await self.course_repo.get(course_id)
        if not course:
            raise ValueError("Course not found.")

        # Teacher owner
        if current_user.role == UserRole.TEACHER:
            if course.teacher_id != current_user.id:
                raise PermissionError("Access denied.")

            return await self.task_repo.get_by_course(
                course_id,
                skip,
                limit
            )

        # Student must be enrolled in the class
        cls = await self.class_repo.get_by_course_id(course.id)

        if not cls:
            raise ValueError("Class not found.")

        enrollment = await self.enroll_repo.find(
            student_id=current_user.id,
            class_id=cls.id
        )

        if not enrollment:
            raise PermissionError("You are not enrolled in this class.")

        return await self.task_repo.get_by_course(
            course_id,
            skip,
            limit
        )

    # =========================
    # GET TASKS BY CLASS
    # =========================
    async def get_tasks_by_class(
        self,
        current_user: User,
        class_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:

        cls = await self.class_repo.get(class_id)

        if not cls:
            raise ValueError("Class not found.")

        course = await self.course_repo.get(cls.course_id)

        if not course:
            raise ValueError("Course not found.")

        # Teacher permission
        if current_user.role == UserRole.TEACHER:

            if course.teacher_id != current_user.id:
                raise PermissionError("Access denied.")

            return await self.task_repo.get_by_course(
                course.id,
                skip,
                limit
            )

        # Student permission
        enrollment = await self.enroll_repo.find(
            student_id=current_user.id,
            class_id=class_id
        )

        if not enrollment:
            raise PermissionError("You are not enrolled in this class.")

        return await self.task_repo.get_by_course(
            course.id,
            skip,
            limit
        )

    # =========================
    # TASK DETAIL
    # =========================
    async def get_task_detail(
        self,
        current_user: User,
        task_id: UUID
    ) -> Task:

        task = await self.task_repo.get(task_id)
        if not task:
            raise ValueError("Task not found.")

        course = await self.course_repo.get(task.course_id)

        # Teacher owner
        if current_user.role == UserRole.TEACHER:
            if course.teacher_id != current_user.id:
                raise PermissionError("Access denied.")
            return task

        # Student must be enrolled
        cls = await self.class_repo.get_by_course_id(course.id)
        if not cls:
            raise ValueError("Class not found.")
        enrollment = await self.enroll_repo.find(
            student_id=current_user.id,
            class_id=cls.id
        )

        if not enrollment:
            raise PermissionError("Access denied.")

        return task

    # =========================
    # UPDATE TASK (Teacher Only)
    # =========================
    async def update_task(
        self,
        current_user: User,
        task_id: UUID,
        data: dict
    ) -> Task:

        task = await self.task_repo.get(task_id)
        if not task:
            raise ValueError("Task not found.")

        course = await self.course_repo.get(task.course_id)

        if course.teacher_id != current_user.id:
            raise PermissionError("You do not own this task.")

        return await self.task_repo.update(task, data)

    # =========================
    # DELETE TASK (Teacher Only)
    # =========================
    async def delete_task(
        self,
        current_user: User,
        task_id: UUID
    ):

        task = await self.task_repo.get(task_id)
        if not task:
            raise ValueError("Task not found.")

        course = await self.course_repo.get(task.course_id)

        if course.teacher_id != current_user.id:
            raise PermissionError("You do not own this task.")

        return await self.task_repo.delete(task_id)