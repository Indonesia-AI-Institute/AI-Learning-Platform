"""
Business logic for authentication.
"""

from backend.auth.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from backend.models.user import User
from backend.repositories.token_blacklist_repository import TokenBlacklistRepository
from backend.repositories.user_repository import UserRepository
from backend.schemas.auth.login_request import LoginRequest
from backend.schemas.auth.register_request import RegisterRequest
from backend.schemas.auth.token_response import TokenResponse
from sqlalchemy.ext.asyncio import AsyncSession

# Precomputed once and verified against on every login where the email
# doesn't exist, so a bcrypt comparison always runs either way — otherwise
# response timing leaks which emails are registered.
_DUMMY_PASSWORD_HASH = hash_password("dummy-password-for-timing-equalization")


class AuthService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.blacklist_repo = TokenBlacklistRepository(db)

    async def register_user(self, data: RegisterRequest) -> TokenResponse:

        existing_email = await self.user_repo.get_by_email(data.email)
        if existing_email:
            raise ValueError("Email already registered")

        hashed_pwd = hash_password(data.password)

        user = User(
            full_name=data.full_name,
            email=data.email,
            hashed_password=hashed_pwd,
            role=data.role,
        )

        user = await self.user_repo.create(user)

        access_token = create_access_token(
            user_id=str(user.id),
            role=user.role.value,
        )

        return TokenResponse(access_token=access_token)

    async def login_user(self, data: LoginRequest) -> TokenResponse:

        user = await self.user_repo.get_by_email(data.email)

        if not user:
            verify_password(data.password, _DUMMY_PASSWORD_HASH)
            raise ValueError("Invalid email or password")

        if user.is_deleted:
            raise ValueError("User account is inactive")

        if not verify_password(data.password, user.hashed_password):
            raise ValueError("Invalid email or password")

        access_token = create_access_token(
            user_id=str(user.id),
            role=user.role.value,
        )

        return TokenResponse(
            access_token=access_token
        )

    async def logout(self, token: str):
        """
        Add token to blacklist.
        Future requests with this token will be rejected.
        """

        await self.blacklist_repo.add_token(token)
