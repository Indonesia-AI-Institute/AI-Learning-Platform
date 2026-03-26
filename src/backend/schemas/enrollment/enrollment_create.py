from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class EnrollmentCreate(BaseModel):
    class_id: UUID