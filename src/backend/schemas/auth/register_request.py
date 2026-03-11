from pydantic import BaseModel, EmailStr, Field
from src.backend.models.user import UserRole


class RegisterRequest(BaseModel):
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        example="John Doe",
    )

    # username: str = Field(
    #     ...,
    #     min_length=8,
    #     max_length=50,
    #     example="johnteacher",
    # )

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