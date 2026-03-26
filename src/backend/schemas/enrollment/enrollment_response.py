from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class EnrollmentResponse(BaseModel):
    id: UUID
    student_id: UUID
    class_id: UUID
    enrolled_at: datetime