from pydantic import BaseModel
from uuid import UUID

class EnrollmentCreate(BaseModel):
    class_id: UUID