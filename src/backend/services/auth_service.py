"""
auth_service.py
===============

Business logic for authentication.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.models.user import User
from src.backend.repositories.user_repository import UserRepository
from src.backend.schemas.auth.register_request import RegisterRequest
from src.backend.schemas.auth.login_request import LoginRequest
from src.backend.repositories.token_blacklist_repository import TokenBlacklistRepository
from src.backend.schemas.auth.token_response import TokenResponse
from src.backend.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
)


class AuthService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.blacklist_repo = TokenBlacklistRepository(db)
    

    # =====================================================
    # REGISTER
    # =====================================================

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

    # =====================================================
    # LOGIN
    # =====================================================

    async def login_user(self, data: LoginRequest) -> TokenResponse:

        user = await self.user_repo.get_by_email(data.email)

        if not user:
            raise ValueError("Invalid email or password")

        # ✅ Correct soft delete check
        if user.is_deleted:
            raise ValueError("User account is inactive")

        # Verify password
        if not verify_password(data.password, user.hashed_password):
            raise ValueError("Invalid email or password")

        access_token = create_access_token(
            user_id=str(user.id),
            role=user.role.value,
        )

        return TokenResponse(
            access_token=access_token
        )
    # =====================================================
    # LOGOUT (BLACKLIST TOKEN)
    # =====================================================

    async def logout(self, token: str):
        """
        Add token to blacklist.
        Future requests with this token will be rejected.
        """

        await self.blacklist_repo.add_token(token)

    