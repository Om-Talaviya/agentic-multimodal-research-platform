"""Tests for persistent UserRepository and User model."""

import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base, bootstrap_default_users
from database.models.user import User as DBUser
from database.repositories.user_repo import UserRepository
from shared.auth import hash_password, verify_password, UserRole


@pytest_asyncio.fixture
async def async_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_create_and_get_user(async_db: AsyncSession):
    repo = UserRepository(async_db)

    password = "SecurePassword123!"
    hashed = hash_password(password)

    user = DBUser(
        username="john_doe",
        email="john@example.com",
        password_hash=hashed,
        role=UserRole.RESEARCHER.value,
        is_active=True,
    )
    created = await repo.create(user)
    await async_db.commit()

    assert created.id is not None
    assert created.username == "john_doe"
    assert created.email == "john@example.com"
    # Ensure password is not stored in plaintext
    assert created.password_hash != password
    assert verify_password(password, created.password_hash)

    # Fetch by ID
    fetched_by_id = await repo.get_by_id(created.id)
    assert fetched_by_id is not None
    assert fetched_by_id.username == "john_doe"

    # Fetch by Username (case-insensitive)
    fetched_by_username = await repo.get_by_username("JOHN_DOE")
    assert fetched_by_username is not None
    assert fetched_by_username.id == created.id

    # Fetch by Email (case-insensitive)
    fetched_by_email = await repo.get_by_email("JOHN@EXAMPLE.COM")
    assert fetched_by_email is not None
    assert fetched_by_email.id == created.id

    # Fetch by username or email
    fetched_by_identifier = await repo.get_by_username_or_email("john@example.com")
    assert fetched_by_identifier is not None
    assert fetched_by_identifier.id == created.id


@pytest.mark.asyncio
async def test_update_user_properties(async_db: AsyncSession):
    repo = UserRepository(async_db)

    user = DBUser(
        username="alice",
        email="alice@example.com",
        password_hash=hash_password("InitialPassword123!"),
        role=UserRole.VIEWER.value,
        is_active=True,
    )
    await repo.create(user)
    await async_db.commit()

    new_hash = hash_password("NewPassword456!")
    updated = await repo.update_user(
        user.id,
        role=UserRole.ADMIN.value,
        is_active=False,
        password_hash=new_hash,
    )
    await async_db.commit()

    assert updated is not None
    assert updated.role == UserRole.ADMIN.value
    assert updated.is_active is False
    assert verify_password("NewPassword456!", updated.password_hash)


@pytest.mark.asyncio
async def test_bootstrap_default_users_is_idempotent(async_db: AsyncSession):
    repo = UserRepository(async_db)

    # First run bootstraps default accounts
    await bootstrap_default_users(async_db)
    await async_db.commit()

    admin = await repo.get_by_username("admin")
    researcher = await repo.get_by_username("researcher")
    viewer = await repo.get_by_username("viewer")

    assert admin is not None
    assert admin.role == UserRole.ADMIN.value
    assert verify_password("AdminPassword123!", admin.password_hash)

    assert researcher is not None
    assert researcher.role == UserRole.RESEARCHER.value

    assert viewer is not None
    assert viewer.role == UserRole.VIEWER.value

    # Second run is idempotent without duplicates
    await bootstrap_default_users(async_db)
    await async_db.commit()

    users = await repo.list_users()
    assert len(users) == 3
