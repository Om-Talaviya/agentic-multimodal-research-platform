"""Authentication and user session routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from api.dependencies import get_current_user
from shared.auth import (
    LoginRequest,
    TokenRefreshRequest,
    TokenResponse,
    User,
    create_access_token,
    create_refresh_token,
    user_registry,
    verify_token,
)
from shared.exceptions import AuthenticationError
from shared.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest) -> TokenResponse:
    """Authenticate with username/email and password to obtain JWT access & refresh tokens."""
    user = user_registry.authenticate(credentials.username, credentials.password)
    if not user:
        logger.warning("Failed login attempt", username=credentials.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

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
async def refresh_token(request: TokenRefreshRequest) -> TokenResponse:
    """Exchange a valid refresh token for a fresh access token."""
    try:
        payload = verify_token(request.refresh_token, expected_type="refresh")
        user = user_registry.get_by_id(payload.sub)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User inactive or no longer exists",
            )

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
