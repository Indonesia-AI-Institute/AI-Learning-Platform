from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.models.user import User, UserRole
from src.backend.models.course import Course
from src.backend.models.enrollment import Enrollment

from src.backend.repositories.course_repository import CourseRepository
from src.backend.repositories.base_repository import BaseRepository


class CourseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.course_repo = CourseRepository(db)
        self.enrollment_repo = BaseRepository(Enrollment, db)

    # =========================
    # CREATE COURSE (Teacher Only)
    # =========================

    async def create_course(
        self,
        current_user: User,
        data: dict
    ) -> Course:

        if current_user.role != UserRole.TEACHER:
            raise PermissionError("Only teachers can create courses.")

        course = Course(
            teacher_id=current_user.id,
            **data
        )

        return await self.course_repo.create(course)

    # =========================
    # GET ALL COURSES
    # =========================

    async def get_my_courses(
        self,
        current_user: User,
        skip: int = 0,
        limit: int = 100
    ) -> List[Course]:

        # Teacher → only their own courses
        if current_user.role == UserRole.TEACHER:
            return await self.course_repo.filter_by(
                teacher_id=current_user.id,
                skip=skip,
                limit=limit
            )

        # Student → only enrolled courses
        enrollments = await self.enrollment_repo.filter_by(
            student_id=current_user.id
        )

        course_ids = [en.course_id for en in enrollments]

        if not course_ids:
            return []

        return await self.course_repo.get_by_ids(
            course_ids=course_ids,
            skip=skip,
            limit=limit
        )

    # =========================
    # GET COURSE DETAIL
    # =========================

    async def get_course_detail(
        self,
        current_user: User,
        course_id: UUID
    ) -> Course:

        db_course = await self.course_repo.get(course_id)
        if not db_course:
            raise ValueError("Course not found.")

        # Teacher owner
        if current_user.role == UserRole.TEACHER:
            if db_course.teacher_id != current_user.id:
                raise PermissionError("Access denied.")
            return db_course

        # Student must be enrolled
        enrollments = await self.enrollment_repo.filter_by(
            student_id=current_user.id,
            course_id=course_id
        )

        if not enrollments:
            raise PermissionError("You are not enrolled in this course.")

        return db_course

    # =========================
    # UPDATE COURSE
    # =========================

    async def update_course(
        self,
        current_user: User,
        course_id: UUID,
        data: dict
    ) -> Course:

        db_course = await self.course_repo.get(course_id)
        if not db_course:
            raise ValueError("Course not found.")

        if db_course.teacher_id != current_user.id:
            raise PermissionError("You do not own this course.")

        return await self.course_repo.update(db_course, data)

    # =========================
    # DELETE COURSE
    # =========================

    async def delete_course(
        self,
        current_user: User,
        course_id: UUID
    ):

        db_course = await self.course_repo.get(course_id)
        if not db_course:
            raise ValueError("Course not found.")

        if db_course.teacher_id != current_user.id:
            raise PermissionError("You do not own this course.")

        return await self.course_repo.delete(course_id)