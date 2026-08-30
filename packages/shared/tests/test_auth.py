"""Unit tests for JWT authentication, password hashing, and user registry."""

from datetime import timedelta
import pytest
from shared.auth import (
    User,
    UserRole,
    create_access_token,
    create_refresh_token,
    hash_password,
    user_registry,
    verify_password,
    verify_token,
)
from shared.exceptions import AuthenticationError


def test_password_hashing_and_verification():
    password = "SuperSecretPassword123!"
    hashed = hash_password(password)

    assert hashed != password
    assert "$" in hashed
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False
    assert verify_password("", hashed) is False
    assert verify_password(password, "") is False


def test_jwt_access_and_refresh_token_lifecycle():
    user = User(
        id="usr_test_123",
        username="test_researcher",
        email="test@research.ai",
        role=UserRole.RESEARCHER,
    )

    access_token = create_access_token(user, expires_delta=timedelta(minutes=15))
    assert isinstance(access_token, str)

    payload = verify_token(access_token, expected_type="access")
    assert payload.sub == "usr_test_123"
    assert payload.username == "test_researcher"
    assert payload.role == UserRole.RESEARCHER
    assert payload.type == "access"

    # Refresh token
    refresh_token = create_refresh_token(user, expires_delta=timedelta(days=1))
    refresh_payload = verify_token(refresh_token, expected_type="refresh")
    assert refresh_payload.sub == "usr_test_123"
    assert refresh_payload.type == "refresh"

    # Type mismatch verification
    with pytest.raises(AuthenticationError):
        verify_token(refresh_token, expected_type="access")


def test_user_registry_authentication():
    user = user_registry.authenticate("admin", "AdminPassword123!")
    assert user is not None
    assert user.role == UserRole.ADMIN
    assert user.has_permission("system:admin") is True

    # Failed auth
    bad_user = user_registry.authenticate("admin", "WrongPassword")
    assert bad_user is None
