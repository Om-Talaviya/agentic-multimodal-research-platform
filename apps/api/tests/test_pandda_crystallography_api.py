"""
API integration tests for Phase 129: PanDDA Fragment Crystallography Endpoints.
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
async def test_pandda_api_flow(test_app: AsyncClient):
    payload = {
        "campaign_name": "KRAS_G12D_PanDDA_Screen",
        "target_protein": "KRAS G12D",
        "total_crystals_soaked": 280,
    }

    # 1. Run PanDDA Screen
    res = await test_app.post("/api/v1/pandda-crystallography/screen", json=payload)
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["status"] == "success"
    assert "screen_id" in data
    screen_id = data["screen_id"]
    assert data["hits_count"] >= 3
    assert data["density_maps_count"] >= 1

    # 2. List screens
    list_res = await test_app.get("/api/v1/pandda-crystallography/screens")
    assert list_res.status_code == 200
    screens = list_res.json()
    assert any(s["id"] == screen_id for s in screens)

    # 3. Retrieve single screen
    get_res = await test_app.get(f"/api/v1/pandda-crystallography/screens/{screen_id}")
    assert get_res.status_code == 200
    detail = get_res.json()
    assert detail["campaign_name"] == "KRAS_G12D_PanDDA_Screen"
    assert len(detail["hits"]) >= 3
    assert len(detail["density_maps"]) >= 1
