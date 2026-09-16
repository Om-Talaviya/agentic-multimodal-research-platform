"""Integration tests for Virtual HTS REST API (Phase 54)."""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from api.dependencies import get_db_session
from database.connection import Base
from main import app


@pytest.fixture
async def async_test_session():
    """Create in-memory SQLite database session for API integration tests."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_vhts_api_full_workflow(async_test_session: AsyncSession):
    async def override_get_db():
        yield async_test_session

    app.dependency_overrides[get_db_session] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Start Screen
        screen_payload = {
            "target_protein_name": "Integration Test EGFR Kinase Domain",
            "pdb_id": "7L11",
            "candidate_smiles_list": [
                "CC(C)N1CCN(CC1)c2cc3ncccc3nc2Nc4ccc(F)cc4",
                "O=C(Nc1ccc(F)cc1)c2cc3ccccc3[nH]2"
            ]
        }
        res = await client.post("/api/v1/vhts/screens", json=screen_payload)
        assert res.status_code == 201
        data = res.json()
        assert data["pdb_id"] == "7L11"
        screen_id = data["id"]

        # 2. Get Screen Details
        get_res = await client.get(f"/api/v1/vhts/screens/{screen_id}")
        assert get_res.status_code == 200
        screen_detail = get_res.json()
        assert len(screen_detail["hits"]) == 2
        assert len(screen_detail["clusters"]) >= 1

        # 3. List Screens
        list_res = await client.get("/api/v1/vhts/screens")
        assert list_res.status_code == 200
        assert any(s["id"] == screen_id for s in list_res.json())

        # 4. Get Metrics
        m_res = await client.get("/api/v1/vhts/metrics")
        assert m_res.status_code == 200
        metrics = m_res.json()
        assert metrics["total_screens"] >= 1
        assert metrics["total_hits_discovered"] >= 2
