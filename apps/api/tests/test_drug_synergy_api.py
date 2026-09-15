"""Integration tests for Drug Repurposing & Synergy REST API (Phase 45)."""
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
        username="oncology_pharmacology_lead",
        email="pharm_lead@dfci.harvard.edu",
        password_hash="mocked",
        role="Researcher",
    )

@pytest.mark.asyncio
async def test_drug_synergy_api_lifecycle(async_test_session: AsyncSession, mock_user: DBUser):
    async def override_get_db():
        yield async_test_session

    async def override_get_user():
        return mock_user

    app.dependency_overrides[get_db_session] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. POST /api/v1/synergy/screens/run
        req_screen = {
            "title": "HCC Sorafenib Combination Screen",
            "disease_indication": "Hepatocellular Carcinoma"
        }
        res_screen = await client.post("/api/v1/synergy/screens/run", json=req_screen)
        assert res_screen.status_code == 201
        data = res_screen.json()
        screen_id = data["id"]
        assert data["total_screened"] == 2450

        # 2. GET /api/v1/synergy/screens
        res_list = await client.get("/api/v1/synergy/screens")
        assert res_list.status_code == 200
        assert len(res_list.json()) >= 1

        # 3. GET /api/v1/synergy/screens/{id}/candidates
        res_cands = await client.get(f"/api/v1/synergy/screens/{screen_id}/candidates")
        assert res_cands.status_code == 200
        assert len(res_cands.json()) >= 3

        # 4. GET /api/v1/synergy/screens/{id}/synergies
        res_syn = await client.get(f"/api/v1/synergy/screens/{screen_id}/synergies")
        assert res_syn.status_code == 200
        assert len(res_syn.json()) >= 2
        assert res_syn.json()[0]["zip_synergy_score"] > 10.0

        # 5. DELETE /api/v1/synergy/screens/{id}
        res_del = await client.delete(f"/api/v1/synergy/screens/{screen_id}")
        assert res_del.status_code == 204

    app.dependency_overrides.clear()
