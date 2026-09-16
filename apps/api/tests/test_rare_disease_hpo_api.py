"""
Integration tests for Rare Disease HPO REST API (Phase 61).
"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from api.dependencies import get_db_session
from database.connection import Base
from main import app


@pytest.fixture
async def async_test_session():
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
async def test_rare_disease_api_workflow(async_test_session: AsyncSession):
    async def override_get_db():
        yield async_test_session

    app.dependency_overrides[get_db_session] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create Case
        res = await client.post(
            "/api/v1/rare-disease/cases",
            json={
                "case_number": "CASE-TEST-002",
                "patient_id": "PT-TEST-002",
                "clinical_summary": "Child with intractable seizures.",
                "age_of_onset": "Infantile",
                "phenotypes": [
                    {"hpo_id": "HP:0001250", "term_name": "Seizures"}
                ],
            },
        )
        assert res.status_code == 201
        data = res.json()
        case_id = data["id"]
        assert len(data["candidate_genes"]) >= 1

        # 2. Get Case Detail
        get_res = await client.get(f"/api/v1/rare-disease/cases/{case_id}")
        assert get_res.status_code == 200
        assert get_res.json()["case_number"] == "CASE-TEST-002"

        # 3. List Cases
        list_res = await client.get("/api/v1/rare-disease/cases")
        assert list_res.status_code == 200
        assert any(c["id"] == case_id for c in list_res.json())
