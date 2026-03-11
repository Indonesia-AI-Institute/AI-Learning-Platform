"""
auth_routes.py
==============

Authentication Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.db.session import get_db
from src.backend.services.auth_service import AuthService

from src.backend.schemas.auth.register_request import RegisterRequest
from src.backend.schemas.auth.login_request import LoginRequest
from src.backend.schemas.auth.token_response import TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])

security = HTTPBearer()


# =====================================================
# REGISTER
# =====================================================

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)

    try:
        return await auth_service.register_user(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# =====================================================
# LOGIN
# =====================================================

@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)

    try:
        return await auth_service.login_user(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# =====================================================
# LOGOUT
# =====================================================

@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)

    token = credentials.credentials

    try:
        await auth_service.logout(token)
        return {"message": "Logged out successfully"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Logout failed",
        )