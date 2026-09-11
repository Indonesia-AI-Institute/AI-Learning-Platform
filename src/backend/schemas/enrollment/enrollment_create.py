from uuid import UUID

from pydantic import BaseModel


class EnrollmentCreate(BaseModel):
    class_id: UUID