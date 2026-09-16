"""Integration tests for Electronic Lab Notebook (ELN) REST API (Phase 53)."""
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
async def test_eln_api_full_workflow(async_test_session: AsyncSession):
    async def override_get_db():
        yield async_test_session

    app.dependency_overrides[get_db_session] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create Notebook
        nb_payload = {
            "title": "Integration Test CRISPR Lab Notebook",
            "author_id": "dr_jane_doe",
            "tags": ["CRISPR", "IntegrationTest"]
        }
        res = await client.post("/api/v1/eln/notebooks", json=nb_payload)
        assert res.status_code == 201
        data = res.json()
        assert data["title"] == "Integration Test CRISPR Lab Notebook"
        nb_id = data["id"]

        # 2. Add Protocol Step Block
        block_payload = {
            "block_type": "PROTOCOL_STEP",
            "content_json": {
                "step_number": 1,
                "title": "Cell Transfection",
                "instructions": "Transfect cells with Cas9 RNP.",
                "parameters": {"voltage": 1150}
            },
            "actor_id": "dr_jane_doe"
        }
        b_res = await client.post(f"/api/v1/eln/notebooks/{nb_id}/blocks", json=block_payload)
        assert b_res.status_code == 201
        b_data = b_res.json()
        assert b_data["block_type"] == "PROTOCOL_STEP"

        # 3. Get Full Notebook Details
        get_res = await client.get(f"/api/v1/eln/notebooks/{nb_id}")
        assert get_res.status_code == 200
        nb_detail = get_res.json()
        assert len(nb_detail["blocks"]) == 1
        assert len(nb_detail["audit_trails"]) >= 2

        # 4. List Notebooks
        list_res = await client.get("/api/v1/eln/notebooks")
        assert list_res.status_code == 200
        assert any(n["id"] == nb_id for n in list_res.json())

        # 5. Witness Sign Notebook
        sign_payload = {
            "witness_id": "dr_principal_investigator",
            "witness_statement": "I have reviewed and witnessed all data entries."
        }
        sign_res = await client.post(f"/api/v1/eln/notebooks/{nb_id}/sign", json=sign_payload)
        assert sign_res.status_code == 200
        assert sign_res.json()["status"] == "WITNESSED"
        assert sign_res.json()["cfr_part11_signed"] is True

        # 6. Get Metrics
        m_res = await client.get("/api/v1/eln/metrics")
        assert m_res.status_code == 200
        metrics = m_res.json()
        assert metrics["total_notebooks"] >= 1
        assert metrics["witnessed_notebooks"] >= 1
