"""Global pytest fixtures and dependency overrides for API tests."""
import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from api.dependencies import get_db, get_db_session, get_current_user
from database.connection import Base
from database.models.user import User as DBUser
from main import app


@pytest.fixture(autouse=True)
async def auto_override_db_and_auth():
    """Automatically provides an in-memory SQLite database and test user for all API tests."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with async_session_factory() as session:
            yield session

    mock_user = DBUser(
        id=uuid.uuid4(),
        username="ci_tester",
        email="ci_tester@platform.local",
        password_hash="mock_hash",
        role="researcher",
        is_active=True,
    )

    async def override_get_current_user():
        return mock_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_db_session] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    yield

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.fixture
def auth_headers():
    """Mock bearer authorization headers for test requests."""
    return {"Authorization": "Bearer mock_valid_jwt_token"}
