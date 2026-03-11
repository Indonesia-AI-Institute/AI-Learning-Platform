from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.models.user import User, UserRole
from src.backend.models.class_model import Class
from src.backend.models.course import Course

from src.backend.repositories.class_repository import ClassRepository
from src.backend.repositories.course_repository import CourseRepository


class ClassService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.class_repo = ClassRepository(db)
        self.course_repo = CourseRepository(db)

    # =========================
    # CREATE CLASS (Teacher Only)
    # =========================

    async def create_class(
        self,
        current_user: User,
        data: dict
    ) -> Class:

        if current_user.role != UserRole.TEACHER:
            raise PermissionError("Only teachers can create class.")

        # Check course ownership
        course = await self.course_repo.get(data["course_id"])
        if not course:
            raise ValueError("Course not found.")

        if course.teacher_id != current_user.id:
            raise PermissionError("You do not own this course.")

        cls = Class(**data)
        return await self.class_repo.create(cls)

    # =========================
    # GET MY CLASSES (Teacher)
    # =========================

    async def get_my_classes(
        self,
        current_user: User,
        skip: int = 0,
        limit: int = 100
    ) -> List[Class]:

        if current_user.role != UserRole.TEACHER:
            raise PermissionError("Only teachers.")

        return await self.class_repo.get_by_teacher(
            teacher_id=current_user.id,
            skip=skip,
            limit=limit
        )

    # =========================
    # UPDATE CLASS
    # =========================

    async def update_class(
        self,
        current_user: User,
        class_id: UUID,
        data: dict
    ) -> Class:

        db_class = await self.class_repo.get(class_id)
        if not db_class:
            raise ValueError("Class not found.")

        # Validate ownership via course
        if db_class.course.teacher_id != current_user.id:
            raise PermissionError("You do not own this class.")

        return await self.class_repo.update(db_class, data)

    # =========================
    # DELETE CLASS
    # =========================

    async def delete_class(
        self,
        current_user: User,
        class_id: UUID
    ):

        db_class = await self.class_repo.get(class_id)
        if not db_class:
            raise ValueError("Class not found.")

        if db_class.course.teacher_id != current_user.id:
            raise PermissionError("You do not own this class.")

        return await self.class_repo.delete(class_id)

    # =========================
    # DETAIL
    # =========================

    async def get_class_detail(
        self,
        current_user: User,
        class_id: UUID
    ) -> Class:

        db_class = await self.class_repo.get(class_id)
        if not db_class:
            raise ValueError("Class not found.")

        # Teacher: only owner
        if current_user.role == UserRole.TEACHER:
            if db_class.course.teacher_id != current_user.id:
                raise PermissionError("Access denied.")
            return db_class

        # Student: allowed to read
        return db_class