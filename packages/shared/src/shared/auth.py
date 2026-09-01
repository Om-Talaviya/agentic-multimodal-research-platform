"""Authentication and authorization framework with JWT, RBAC, and password hashing."""

from datetime import datetime, timedelta, timezone
from enum import Enum
import hashlib
import hmac
import os
import secrets
from typing import Any, Dict, List, Optional
from jose import JWTError, jwt
from pydantic import BaseModel, Field
from shared.config import settings
from shared.exceptions import AuthenticationError, AuthorizationError
from shared.logging import get_logger

logger = get_logger(__name__)

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 7


class UserRole(str, Enum):
    """User access roles for Role-Based Access Control (RBAC)."""

    ADMIN = "admin"
    RESEARCHER = "researcher"
    VIEWER = "viewer"


ROLE_PERMISSIONS: Dict[UserRole, set[str]] = {
    UserRole.ADMIN: {
        "research:create",
        "research:read",
        "research:delete",
        "documents:upload",
        "documents:read",
        "documents:delete",
        "system:admin",
        "metrics:read",
    },
    UserRole.RESEARCHER: {
        "research:create",
        "research:read",
        "documents:upload",
        "documents:read",
        "metrics:read",
    },
    UserRole.VIEWER: {
        "research:read",
        "documents:read",
        "metrics:read",
    },
}


class User(BaseModel):
    """Authenticated user entity."""

    id: str
    username: str
    email: str
    role: UserRole = UserRole.RESEARCHER
    is_active: bool = True
    hashed_password: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def has_permission(self, permission: str) -> bool:
        """Check if user role possesses specific permission."""
        perms = ROLE_PERMISSIONS.get(self.role, set())
        return permission in perms

    @classmethod
    def from_db(cls, db_user: Any) -> "User":
        """Convert a SQLAlchemy User database model to a Pydantic User entity."""
        return cls(
            id=str(db_user.id),
            username=db_user.username,
            email=db_user.email,
            role=UserRole(db_user.role) if isinstance(db_user.role, str) else db_user.role,
            is_active=db_user.is_active,
            hashed_password=getattr(db_user, "password_hash", None) or getattr(db_user, "hashed_password", None),
            created_at=db_user.created_at if hasattr(db_user, "created_at") and db_user.created_at else datetime.now(timezone.utc),
        )


class TokenPayload(BaseModel):
    """Decoded JWT claims payload."""

    sub: str
    username: str
    email: str
    role: UserRole
    type: str = "access"  # access or refresh
    exp: int
    iat: int


class TokenResponse(BaseModel):
    """OAuth2 / JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]


class LoginRequest(BaseModel):
    """Login credential payload."""

    username: str
    password: str


class TokenRefreshRequest(BaseModel):
    """Token refresh request."""

    refresh_token: str


# --- Password Hashing & Verification using PBKDF2-HMAC-SHA256 ---

def hash_password(password: str, salt: Optional[str] = None) -> str:
    """Hash password securely using PBKDF2-HMAC-SHA256 with 100,000 iterations."""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    ).hex()
    return f"{salt}${hashed}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against stored salt$hash string."""
    if not hashed_password or "$" not in hashed_password:
        return False
    salt, original_hash = hashed_password.split("$", 1)
    computed_hash = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    ).hex()
    return hmac.compare_digest(original_hash, computed_hash)


# --- JWT Token Generation & Verification ---

def create_access_token(
    user: User,
    expires_delta: Optional[timedelta] = None,
    secret_key: Optional[str] = None,
) -> str:
    """Generate signed JWT access token."""
    key = secret_key or settings.secret_key
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    payload = {
        "sub": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, key, algorithm=JWT_ALGORITHM)


def create_refresh_token(
    user: User,
    expires_delta: Optional[timedelta] = None,
    secret_key: Optional[str] = None,
) -> str:
    """Generate signed JWT refresh token."""
    key = secret_key or settings.secret_key
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))

    payload = {
        "sub": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, key, algorithm=JWT_ALGORITHM)


def verify_token(
    token: str,
    expected_type: str = "access",
    secret_key: Optional[str] = None,
) -> TokenPayload:
    """Verify and decode JWT token."""
    key = secret_key or settings.secret_key
    try:
        payload_dict = jwt.decode(token, key, algorithms=[JWT_ALGORITHM], options={"verify_exp": False})
        exp = payload_dict.get("exp")
        if exp is not None and datetime.now(timezone.utc).timestamp() > exp:
            raise JWTError("Signature has expired.")

        token_type = payload_dict.get("type", "access")
        if token_type != expected_type:
            raise AuthenticationError(f"Invalid token type: expected '{expected_type}', got '{token_type}'")

        return TokenPayload(
            sub=payload_dict["sub"],
            username=payload_dict["username"],
            email=payload_dict["email"],
            role=UserRole(payload_dict["role"]),
            type=token_type,
            exp=payload_dict["exp"],
            iat=payload_dict["iat"],
        )
    except JWTError as e:
        logger.warning("Token verification failed", error=str(e))
        raise AuthenticationError(f"Could not validate credentials: {str(e)}")


# --- In-Memory Users Registry for Auth Service ---

class UserRegistry:
    """In-memory user account store for authentication."""

    def __init__(self) -> None:
        self._users_by_id: Dict[str, User] = {}
        self._users_by_username: Dict[str, User] = {}
        self._users_by_email: Dict[str, User] = {}

    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        role: UserRole = UserRole.RESEARCHER,
        user_id: Optional[str] = None,
    ) -> User:
        """Register a new user with hashed password."""
        uid = user_id or f"usr_{secrets.token_hex(6)}"
        hashed = hash_password(password)
        user = User(
            id=uid,
            username=username,
            email=email,
            role=role,
            is_active=True,
            hashed_password=hashed,
        )
        self._users_by_id[user.id] = user
        self._users_by_username[user.username.lower()] = user
        self._users_by_email[user.email.lower()] = user
        return user

    def authenticate(self, username_or_email: str, password: str) -> Optional[User]:
        """Authenticate user by username or email and password."""
        key = username_or_email.lower().strip()
        user = self._users_by_username.get(key) or self._users_by_email.get(key)
        if not user or not user.hashed_password or not user.is_active:
            return None
        if verify_password(password, user.hashed_password):
            return user
        return None

    def get_by_id(self, user_id: str) -> Optional[User]:
        """Retrieve user by ID."""
        return self._users_by_id.get(user_id)

    def get_by_username(self, username: str) -> Optional[User]:
        """Retrieve user by username."""
        return self._users_by_username.get(username.lower().strip())


# Global default user registry with standard demo/system accounts
user_registry = UserRegistry()

# Seed default demo accounts
user_registry.register_user(
    username="admin",
    email="admin@platform.ai",
    password="AdminPassword123!",
    role=UserRole.ADMIN,
    user_id="usr_admin_001",
)
user_registry.register_user(
    username="researcher",
    email="researcher@platform.ai",
    password="ResearcherPassword123!",
    role=UserRole.RESEARCHER,
    user_id="usr_researcher_001",
)
user_registry.register_user(
    username="viewer",
    email="viewer@platform.ai",
    password="ViewerPassword123!",
    role=UserRole.VIEWER,
    user_id="usr_viewer_001",
)
