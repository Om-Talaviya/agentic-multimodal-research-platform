"""Integration tests for AI Scientist REST API (Phase 50)."""
import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.connection import Base
from database.models.user import User as DBUser
from api.dependencies import get_current_user, get_db_session
from main import app

@pytest.fixture
async def async_test_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session
    
    await engine.dispose()

@pytest.fixture
def mock_user():
    return DBUser(
        id=uuid.uuid4(),
        username="ai_scientist_lead",
        email="scientist@deepmind.com",
        password_hash="mocked",
        role="Researcher",
    )

@pytest.mark.asyncio
async def test_ai_scientist_api_lifecycle(async_test_session: AsyncSession, mock_user: DBUser):
    async def override_get_db():
        yield async_test_session

    async def override_get_user():
        return mock_user

    app.dependency_overrides[get_db_session] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_user

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post("/api/v1/ai-scientist/run", json={
                "title": "Pan-KRAS Discovery",
                "research_domain": "Structural Therapeutics",
                "goal_statement": "Discover and validate novel modalities",
                "cycles_count": 3
            })
            assert res.status_code == 201
            data = res.json()
            assert "id" in data
            program_id = data["id"]

            list_res = await client.get("/api/v1/ai-scientist/programs")
            assert list_res.status_code == 200
            assert len(list_res.json()) >= 1

            detail_res = await client.get(f"/api/v1/ai-scientist/programs/{program_id}")
            assert detail_res.status_code == 200
            detail = detail_res.json()
            assert len(detail["cycles"]) >= 1
            assert len(detail["breakthroughs"]) >= 1
    finally:
        app.dependency_overrides.clear()
