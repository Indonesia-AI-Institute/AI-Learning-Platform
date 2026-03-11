from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        example="john@example.com",
    )

    password: str = Field(
        ...,
        min_length=8,
        example="strongpassword123",
    )