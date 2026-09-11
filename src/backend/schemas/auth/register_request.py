from backend.models.user import UserRole
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        example="John Doe",
    )

    email: EmailStr = Field(
        ...,
        example="john@example.com",
    )

    password: str = Field(
        ...,
        min_length=8,
        example="strongpassword123",
    )

    role: UserRole