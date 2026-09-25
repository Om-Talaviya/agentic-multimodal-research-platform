"""Tests for Phase 187: Milestone v2.1 API."""

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
async def test_milestone_v2_1_synthesis_endpoint(async_client: AsyncClient):
    payload = {
        "name": "Planetary Research Meta-Synthesis 2026",
        "mission_scope": "Planetary Multimodal Autonomous Synthesis",
        "active_subsystems_count": 187,
        "global_cross_correlation_input": 0.982,
    }

    response = await async_client.post("/api/v1/milestone-v2-1/synthesize", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Planetary Research Meta-Synthesis 2026"
    assert "telemetries" in data
    assert "planetary_runs" in data
    assert len(data["telemetries"]) >= 5

    list_resp = await async_client.get("/api/v1/milestone-v2-1/studies")
    assert list_resp.status_code == 200
    studies = list_resp.json()
    assert len(studies) >= 1
