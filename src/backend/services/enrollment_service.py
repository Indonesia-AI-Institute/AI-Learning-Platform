from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.models.enrollment import Enrollment
from src.backend.models.user import User, UserRole
from src.backend.models.class_model import Class
from src.backend.repositories.enrollment_repository import EnrollmentRepository
from src.backend.repositories.class_repository import ClassRepository


class EnrollmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.enroll_repo = EnrollmentRepository(db)
        self.class_repo = ClassRepository(db)

    # ===============================
    # STUDENT ENROLL
    # ===============================
    async def enroll_student(
        self,
        student: User,
        class_id: UUID
    ) -> Enrollment:

        if student.role != UserRole.STUDENT:
            raise PermissionError("Only students can enroll in class.")

        cls = await self.class_repo.get(class_id)
        if not cls:
            raise ValueError("Class not found.")

        if not cls.is_active:
            raise ValueError("Class is not active.")

        existing = await self.enroll_repo.find(student.id, class_id)
        if existing:
            raise ValueError("Already enrolled in this class.")

        enrollment = Enrollment(
            student_id=student.id,
            class_id=class_id
        )

        return await self.enroll_repo.create(enrollment)

    # ===============================
    # STUDENT VIEW OWN ENROLLMENTS
    # ===============================
    async def get_student_enrollments(
        self,
        student: User,
        skip: int = 0,
        limit: int = 100
    ) -> List[Enrollment]:

        if student.role != UserRole.STUDENT:
            raise PermissionError("Only students can view enrollments.")

        return await self.enroll_repo.get_by_student(
            student.id,
            skip=skip,
            limit=limit
        )

    # ===============================
    # TEACHER VIEW CLASS ENROLLMENTS
    # ===============================
    async def get_class_enrollments(
        self,
        current_user: User,
        class_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Enrollment]:

        if current_user.role != UserRole.TEACHER:
            raise PermissionError("Only teachers can view class enrollments.")

        cls = await self.class_repo.get_by_id_and_teacher(
            class_id,
            current_user.id
        )

        if not cls:
            raise PermissionError("You do not own this class or class not found.")

        return await self.enroll_repo.get_by_class(
            class_id,
            skip=skip,
            limit=limit
        )