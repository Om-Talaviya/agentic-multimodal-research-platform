"""Integration tests for Pharmacovigilance REST API (Phase 49)."""
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
        username="pv_lead",
        email="pv@ema.europa.eu",
        password_hash="mocked",
        role="Researcher",
    )

@pytest.mark.asyncio
async def test_pharmacovigilance_api_lifecycle(async_test_session: AsyncSession, mock_user: DBUser):
    async def override_get_db():
        yield async_test_session

    async def override_get_user():
        return mock_user

    app.dependency_overrides[get_db_session] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_user

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post("/api/v1/pharmacovigilance/detect", json={
                "drug_name": "Trastuzumab Deruxtecan",
                "corpus_size": 1250000
            })
            assert res.status_code == 201
            data = res.json()
            assert "id" in data
            corpus_id = data["id"]

            list_res = await client.get("/api/v1/pharmacovigilance/corpora")
            assert list_res.status_code == 200
            assert len(list_res.json()) >= 1

            detail_res = await client.get(f"/api/v1/pharmacovigilance/corpora/{corpus_id}")
            assert detail_res.status_code == 200
            detail = detail_res.json()
            assert len(detail["signals"]) >= 1
            assert len(detail["signals"][0]["metrics"]) >= 1
    finally:
        app.dependency_overrides.clear()
