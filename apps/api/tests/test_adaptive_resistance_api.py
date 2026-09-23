"""API integration tests for Phase 130: Precision Oncology Adaptive Resistance Endpoints."""

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
async def test_adaptive_resistance_api_flow(test_app: AsyncClient):
    payload = {
        "name": "Colorectal Cancer 5-FU Clonal Evolution",
        "cancer_type": "Colorectal Adenocarcinoma",
        "patient_id": "CRC-7890",
        "description": "Adaptive dose-skipping versus continuous 5-FU simulation",
        "cycles": 4,
        "adaptive_threshold": 0.5,
    }

    # 1. Run simulation
    res = await test_app.post("/api/v1/adaptive-resistance/simulate", json=payload)
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["status"] == "success"
    assert "study_id" in data
    study_id = data["study_id"]
    assert data["total_trajectories"] >= 4
    assert len(data["recommendations"]) > 0

    # 2. List studies
    list_res = await test_app.get("/api/v1/adaptive-resistance/studies")
    assert list_res.status_code == 200
    studies = list_res.json()
    assert any(s["id"] == study_id for s in studies)

    # 3. Retrieve study detail
    get_res = await test_app.get(f"/api/v1/adaptive-resistance/studies/{study_id}")
    assert get_res.status_code == 200
    detail = get_res.json()
    assert detail["name"] == "Colorectal Cancer 5-FU Clonal Evolution"
    assert len(detail["clonal_lineages"]) >= 2
    assert len(detail["trajectories"]) >= 4
