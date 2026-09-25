"""Tests for Phase 180: CRISPR Prime Editing pegRNA API."""

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
async def test_pegdna_simulation_endpoint(async_client: AsyncClient):
    payload = {
        "name": "HBB API Test",
        "target_gene": "HBB",
        "intended_mutation_type": "point_substitution",
        "pbs_length_nt": 13,
        "rtt_length_nt": 15,
        "nick_to_edit_distance_bp": 3,
        "pe_system_version": "PEmax_epegRNA",
    }

    response = await async_client.post("/api/v1/crispr-prime-editing-pegdna/simulate", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "HBB API Test"
    assert "pegdna_candidates" in data
    assert "flap_kinetics" in data

    list_resp = await async_client.get("/api/v1/crispr-prime-editing-pegdna/studies")
    assert list_resp.status_code == 200
    studies = list_resp.json()
    assert len(studies) >= 1
