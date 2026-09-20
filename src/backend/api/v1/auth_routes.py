from backend.api.deps import get_current_user
from backend.core.config import settings
from backend.db.session import get_db
from backend.models.user import User
from backend.schemas.auth.login_request import LoginRequest
from backend.schemas.auth.register_request import RegisterRequest
from backend.schemas.auth.token_response import TokenResponse
from backend.schemas.auth.user_response import UserResponse
from backend.services.auth_service import AuthService
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["Auth"])

security = HTTPBearer(auto_error=False)

COOKIE_NAME = "access_token"
COOKIE_MAX_AGE = 60 * 60 * 24  # 24 hours


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)

    try:
        token_data = await auth_service.register_user(request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    response.set_cookie(
        key=COOKIE_NAME,
        value=token_data.access_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=COOKIE_MAX_AGE,
        domain=settings.COOKIE_DOMAIN or None,
    )

    return token_data


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)

    try:
        token_data = await auth_service.login_user(request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    response.set_cookie(
        key=COOKIE_NAME,
        value=token_data.access_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=COOKIE_MAX_AGE,
        domain=settings.COOKIE_DOMAIN or None,
    )

    return token_data


@router.post("/logout")
async def logout(
    response: Response,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)

    token = credentials.credentials if credentials else None

    if token:
        try:
            await auth_service.logout(token)
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Logout failed")

    response.delete_cookie(
        key=COOKIE_NAME,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        domain=settings.COOKIE_DOMAIN or None,
    )

    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """
    Get current authenticated user info.
    Used by frontend Navbar/Sidebar to display user details.
    """
    return current_user