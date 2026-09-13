"""
Unit tests for Developer API Key Repository & Rate Limiting (Phase 25).
"""

import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.models.user import User as DBUser
from database.repositories.user_repo import UserRepository
from database.repositories.api_key_repo import ApiKeyRepository
from shared.auth import hash_password, UserRole


@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_factory() as session:
        # Create test user
        user_repo = UserRepository(session)
        user = DBUser(
            id=uuid.UUID("33333333-3333-3333-3333-333333333333"),
            username="dev_tester",
            email="tester@dev.ai",
            password_hash=hash_password("DevPass123!"),
            role=UserRole.RESEARCHER.value,
            is_active=True,
        )
        await user_repo.create(user)
        await session.commit()
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_api_key_create_and_authenticate(async_session: AsyncSession):
    repo = ApiKeyRepository()
    user_id = uuid.UUID("33333333-3333-3333-3333-333333333333")

    # Create key
    key_record, raw_key = await repo.create_api_key(
        session=async_session,
        user_id=user_id,
        name="Test Production Key",
        scopes=["research:read", "research:write"],
        rate_limit_tier="pro",
        expires_in_days=30,
    )

    assert key_record.name == "Test Production Key"
    assert key_record.rate_limit_tier == "pro"
    assert key_record.rate_limit_rpm == 300
    assert raw_key.startswith("amrp_live_")
    assert key_record.is_active is True

    # Authenticate with valid key
    auth_record = await repo.authenticate_api_key(async_session, raw_key)
    assert auth_record is not None
    assert auth_record.id == key_record.id
    assert auth_record.last_used_at is not None

    # Authenticate with invalid key
    invalid_auth = await repo.authenticate_api_key(async_session, "amrp_live_invalidkey123456789")
    assert invalid_auth is None


@pytest.mark.asyncio
async def test_api_key_revocation_and_expiration(async_session: AsyncSession):
    repo = ApiKeyRepository()
    user_id = uuid.UUID("33333333-3333-3333-3333-333333333333")

    key_record, raw_key = await repo.create_api_key(
        session=async_session,
        user_id=user_id,
        name="Key To Revoke",
        rate_limit_tier="free",
    )

    # Revoke key
    revoked = await repo.revoke_api_key(async_session, key_id=key_record.id, user_id=user_id)
    assert revoked is True

    # Authenticate should fail on revoked key
    auth_after_revoke = await repo.authenticate_api_key(async_session, raw_key)
    assert auth_after_revoke is None


@pytest.mark.asyncio
async def test_api_key_list_and_delete(async_session: AsyncSession):
    repo = ApiKeyRepository()
    user_id = uuid.UUID("33333333-3333-3333-3333-333333333333")

    k1, _ = await repo.create_api_key(async_session, user_id, "Key 1")
    k2, _ = await repo.create_api_key(async_session, user_id, "Key 2")

    keys = await repo.list_api_keys(async_session, user_id=user_id)
    assert len(keys) >= 2
    key_ids = [k.id for k in keys]
    assert k1.id in key_ids
    assert k2.id in key_ids

    # Delete k1
    deleted = await repo.delete_api_key(async_session, key_id=k1.id, user_id=user_id)
    assert deleted is True

    keys_after = await repo.list_api_keys(async_session, user_id=user_id)
    assert k1.id not in [k.id for k in keys_after]


def test_sliding_window_rate_limiter():
    key_id = str(uuid.uuid4())
    rpm_limit = 3

    # First 3 requests allowed
    ok1, rem1, _ = ApiKeyRepository.check_rate_limit(key_id, rpm=rpm_limit)
    assert ok1 is True
    assert rem1 == 2

    ok2, rem2, _ = ApiKeyRepository.check_rate_limit(key_id, rpm=rpm_limit)
    assert ok2 is True
    assert rem2 == 1

    ok3, rem3, _ = ApiKeyRepository.check_rate_limit(key_id, rpm=rpm_limit)
    assert ok3 is True
    assert rem3 == 0

    # 4th request in same second should be throttled
    ok4, rem4, retry_after = ApiKeyRepository.check_rate_limit(key_id, rpm=rpm_limit)
    assert ok4 is False
    assert rem4 == 0
    assert retry_after > 0
