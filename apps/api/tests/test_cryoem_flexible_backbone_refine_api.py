"""Tests for Phase 214: Autonomous Cryo-EM Continuous Flexible Backbone Motion & Deep Non-Rigid Fitting Engine API."""

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
async def test_cryoem_flexible_backbone_refine_api(async_client: AsyncClient):
    payload = {
        "name": "Autonomous Cryo-EM Continuous Flexible Backbone Motion & Deep Non-Rigid Fitting Engine API Test",
        "target_specimen": "Human Patient Cohort Sample",
        "analytical_modality": "cryoem-flexible-backbone-refine",
        "input_scale": 1.0,
    }

    response = await async_client.post("/api/v1/cryoem-flexible-backbone-refine/analyze", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Autonomous Cryo-EM Continuous Flexible Backbone Motion & Deep Non-Rigid Fitting Engine API Test"
    assert "item_profiles" in data
    assert "metric_traces" in data
    assert len(data["item_profiles"]) >= 3

    list_resp = await async_client.get("/api/v1/cryoem-flexible-backbone-refine/studies")
    assert list_resp.status_code == 200
    studies = list_resp.json()
    assert len(studies) >= 1
