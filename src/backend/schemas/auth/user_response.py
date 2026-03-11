from datetime import datetime
from pydantic import BaseModel, EmailStr

from src.backend.models.user import UserRole


class UserResponse(BaseModel):
    id: str
    full_name: str
    username: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # allow reading from SQLAlchemy model