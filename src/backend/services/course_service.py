from typing import List
from uuid import UUID

from backend.models.course import Course
from backend.models.enrollment import Enrollment
from backend.models.user import User, UserRole
from backend.repositories.base_repository import BaseRepository
from backend.repositories.class_repository import ClassRepository
from backend.repositories.course_repository import CourseRepository
from sqlalchemy.ext.asyncio import AsyncSession


class CourseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.course_repo = CourseRepository(db)
        self.enrollment_repo = BaseRepository(Enrollment, db)
        self.class_repo = ClassRepository(db)

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

    # Teacher: own courses. Student: courses from their enrolled classes.
    async def get_my_courses(
        self,
        current_user: User,
        skip: int = 0,
        limit: int = 100
    ) -> List[Course]:

        if current_user.role == UserRole.TEACHER:
            return await self.course_repo.get_by_teacher(
                teacher_id=current_user.id,
                skip=skip,
                limit=limit
            )

        # Student: get enrolled class_ids, then get course_ids from those classes
        enrollments = await self.enrollment_repo.filter_by(
            student_id=current_user.id
        )

        if not enrollments:
            return []

        class_ids = [en.class_id for en in enrollments]

        classes = await self.class_repo.get_by_ids(class_ids)
        course_ids = list({cls.course_id for cls in classes})

        if not course_ids:
            return []

        return await self.course_repo.get_by_ids(
            course_ids=course_ids,
            skip=skip,
            limit=limit
        )

    async def get_all_active_courses(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Course]:

        return await self.course_repo.get_all_active(
            skip=skip,
            limit=limit
        )

    async def get_course_detail(
        self,
        current_user: User,
        course_id: UUID
    ) -> Course:

        db_course = await self.course_repo.get(course_id)
        if not db_course:
            raise ValueError("Course not found.")

        if current_user.role == UserRole.TEACHER:
            if db_course.teacher_id != current_user.id:
                raise PermissionError("Access denied.")
            return db_course

        # Student: allowed to view any course (for browsing)
        return db_course

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