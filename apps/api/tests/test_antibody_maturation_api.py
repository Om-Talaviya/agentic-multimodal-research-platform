"""
API integration tests for Phase 127: Antibody Affinity Maturation Endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from api.dependencies import get_db
from main import app


@pytest.fixture
async def test_app():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def override_get_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.asyncio
async def test_antibody_maturation_api_flow(test_app: AsyncClient):
    payload = {
        "candidate_name": "mAb-Trop2-Evol-01",
        "target_antigen": "TROP2 Extracellular Domain",
        "parental_kd_nm": 14.2,
        "evolution_rounds": 4,
    }

    # 1. Mature antibody
    res = await test_app.post("/api/v1/antibody-maturation/mature", json=payload)
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["status"] == "success"
    assert "campaign_id" in data
    campaign_id = data["campaign_id"]
    assert data["variants_count"] >= 4
    assert data["contacts_count"] >= 3

    # 2. List campaigns
    list_res = await test_app.get("/api/v1/antibody-maturation/campaigns")
    assert list_res.status_code == 200
    campaigns = list_res.json()
    assert any(c["id"] == campaign_id for c in campaigns)

    # 3. Retrieve single campaign
    get_res = await test_app.get(f"/api/v1/antibody-maturation/campaigns/{campaign_id}")
    assert get_res.status_code == 200
    detail = get_res.json()
    assert detail["candidate_name"] == "mAb-Trop2-Evol-01"
    assert len(detail["variants"]) >= 4
    assert len(detail["contacts"]) >= 3
