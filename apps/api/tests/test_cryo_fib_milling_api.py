"""Tests for Phase 414: Autonomous Cryo-FIB Milling & In-Situ Lamella Thickness Optimization Engine API."""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base, get_db_session
from main import app


@pytest_asyncio.fixture
async def async_client():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db_session():
        async with session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db_session] = override_get_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.mark.asyncio
async def test_cryo_fib_milling_api(async_client: AsyncClient):
    payload = {
        "name": "Autonomous Cryo-FIB Milling In-Situ Lamella Thinning API Test",
        "target_specimen": "Vitreous Cellular Cryo-Lamella",
        "analytical_modality": "cryo-fib-milling",
        "input_scale": 1.0,
    }

    response = await async_client.post("/api/v1/cryo-fib-milling/analyze", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Autonomous Cryo-FIB Milling In-Situ Lamella Thinning API Test"
    assert data["in_situ_lamella_thickness_nm"] < 150.0
    assert data["curtaining_artifact_suppression_ratio"] > 0.90
    assert "item_profiles" in data
    assert "metric_traces" in data
    assert len(data["item_profiles"]) >= 3

    study_id = data["id"]
    get_resp = await async_client.get(f"/api/v1/cryo-fib-milling/studies/{study_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == study_id

    list_resp = await async_client.get("/api/v1/cryo-fib-milling/studies")
    assert list_resp.status_code == 200
    studies = list_resp.json()
    assert len(studies) >= 1
