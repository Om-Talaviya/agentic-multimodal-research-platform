"""Global pytest fixtures and dependency overrides for API tests."""
import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from api.dependencies import get_db, get_db_session, get_current_user
from database.connection import Base
from database.models.user import User as DBUser
from shared.auth import UserRole
from main import app


class MockRole:
    value = "researcher"

    def __str__(self):
        return "researcher"

    def __eq__(self, other):
        return str(other) == "researcher"


@pytest_asyncio.fixture
async def auth_headers():
    """Provides mock auth headers and sets up in-memory DB + user session for the test."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    mock_user = DBUser(
        id=uuid.uuid4(),
        username="ci_tester",
        email="ci_tester@platform.local",
        password_hash="mock_hash",
        role="researcher",
        is_active=True,
    )
    mock_user.role = MockRole()

    async def override_get_current_user():
        return mock_user

    orig_get_db = app.dependency_overrides.get(get_db)
    orig_get_db_session = app.dependency_overrides.get(get_db_session)
    orig_get_current_user = app.dependency_overrides.get(get_current_user)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_db_session] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    yield {"Authorization": "Bearer mock_valid_jwt_token"}

    if orig_get_db is not None:
        app.dependency_overrides[get_db] = orig_get_db
    else:
        app.dependency_overrides.pop(get_db, None)

    if orig_get_db_session is not None:
        app.dependency_overrides[get_db_session] = orig_get_db_session
    else:
        app.dependency_overrides.pop(get_db_session, None)

    if orig_get_current_user is not None:
        app.dependency_overrides[get_current_user] = orig_get_current_user
    else:
        app.dependency_overrides.pop(get_current_user, None)

    await engine.dispose()
