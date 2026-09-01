"""Authentication and user session routes."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_current_user
from database.connection import get_db_session
from database.repositories import UserRepository
from shared.auth import (
    LoginRequest,
    TokenRefreshRequest,
    TokenResponse,
    User,
    create_access_token,
    create_refresh_token,
    verify_password,
    verify_token,
)
from shared.exceptions import AuthenticationError
from shared.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    """Authenticate with username/email and password to obtain JWT access & refresh tokens."""
    repo = UserRepository(session)
    db_user = await repo.get_by_username_or_email(credentials.username)
    if not db_user or not db_user.is_active or not verify_password(credentials.password, db_user.password_hash):
        logger.warning("Failed login attempt", username=credentials.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = User.from_db(db_user)
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    logger.info("User logged in successfully", username=user.username, role=user.role.value)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=60 * 24 * 60,  # 24 hours in seconds
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
        },
    )


@router.post("/token/refresh", response_model=TokenResponse)
async def refresh_token(
    request: TokenRefreshRequest,
    session: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    """Exchange a valid refresh token for a fresh access token."""
    try:
        payload = verify_token(request.refresh_token, expected_type="refresh")
        repo = UserRepository(session)
        db_user = None
        try:
            db_user = await repo.get_by_id(UUID(payload.sub))
        except (ValueError, TypeError):
            db_user = await repo.get_by_username(payload.username)

        if not db_user or not db_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User inactive or no longer exists",
            )

        user = User.from_db(db_user)
        new_access_token = create_access_token(user)
        new_refresh_token = create_refresh_token(user)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=60 * 24 * 60,
            user={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
            },
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)) -> dict:
    """Retrieve current authenticated user profile and permissions."""
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value,
        "permissions": [p for p in ["research:create", "research:read", "documents:upload"] if user.has_permission(p)],
    }
