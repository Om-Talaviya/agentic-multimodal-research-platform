"""Tests for Phase 178: ADC DAR Optimization API."""

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
async def test_adc_dar_simulation_endpoint(async_client: AsyncClient):
    payload = {
        "name": "Trastuzumab-vcMMAE Phase 178 API Test",
        "antibody_name": "Trastuzumab",
        "payload_name": "vc-MMAE",
        "target_dar": 4.0,
        "linker_type": "cleavable_val_cit",
        "conjugation_chemistry": "cysteine_maleimide",
        "payload_logp": 2.8,
        "reaction_stoichiometry": 4.5,
    }

    response = await async_client.post("/api/v1/adc-dar-optimization/simulate", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Trastuzumab-vcMMAE Phase 178 API Test"
    assert "species_distribution" in data
    assert "aggregation_kinetics" in data

    list_resp = await async_client.get("/api/v1/adc-dar-optimization/studies")
    assert list_resp.status_code == 200
    studies = list_resp.json()
    assert len(studies) >= 1
