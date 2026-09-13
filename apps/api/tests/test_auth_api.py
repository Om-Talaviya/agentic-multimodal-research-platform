"""Integration tests for persistent Authentication API endpoints."""

import pytest
import pytest_asyncio
import httpx
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from main import app
from database.connection import Base, bootstrap_default_users, get_db_session
from database.models.user import User as DBUser
from database.repositories.user_repo import UserRepository
from shared.auth import UserRole, hash_password


@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db_session():
        async with session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    # Bootstrap default users
    async with session_maker() as session:
        await bootstrap_default_users(session)
        await session.commit()

    app.dependency_overrides[get_db_session] = override_get_db_session

    yield session_maker

    app.dependency_overrides.pop(get_db_session, None)
    await engine.dispose()


@pytest.mark.asyncio
async def test_auth_login_success_and_me():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Login with bootstrapped admin account
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "AdminPassword123!"},
        )
        assert login_resp.status_code == 200
        data = login_resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["username"] == "admin"
        assert data["user"]["role"] == "admin"

        token = data["access_token"]
        refresh_tok = data["refresh_token"]

        # 2. Access /api/v1/auth/me with bearer token
        me_resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_resp.status_code == 200
        me_data = me_resp.json()
        assert me_data["username"] == "admin"
        assert me_data["role"] == "admin"

        # 3. Refresh token
        refresh_resp = await client.post(
            "/api/v1/auth/token/refresh",
            json={"refresh_token": refresh_tok},
        )
        assert refresh_resp.status_code == 200
        ref_data = refresh_resp.json()
        assert "access_token" in ref_data


@pytest.mark.asyncio
async def test_auth_login_invalid_credentials():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "WrongPassword!"},
        )
        assert resp.status_code == 401


@pytest.mark.asyncio
async def test_auth_inactive_user_cannot_login(setup_test_db):
    session_maker = setup_test_db
    # Create an inactive user in test database
    async with session_maker() as session:
        repo = UserRepository(session)
        inactive = DBUser(
            username="disabled_user",
            email="disabled@example.com",
            password_hash=hash_password("Password123!"),
            role=UserRole.VIEWER.value,
            is_active=False,
        )
        await repo.create(inactive)
        await session.commit()

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "disabled_user", "password": "Password123!"},
        )
        assert resp.status_code == 401
