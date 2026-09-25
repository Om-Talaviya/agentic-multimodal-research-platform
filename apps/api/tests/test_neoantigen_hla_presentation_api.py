"""Tests for Phase 185: Tumor Neoantigen API."""

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
async def test_neoantigen_simulation_endpoint(async_client: AsyncClient):
    payload = {
        "name": "Patient MEL-402 API Test",
        "patient_tumor_id": "TUMOR-MEL-402",
        "patient_hla_alleles": "HLA-A*02:01, HLA-A*24:02, HLA-B*07:02",
        "somatic_mutations_count": 45,
    }

    response = await async_client.post("/api/v1/neoantigen-hla-presentation/simulate", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Patient MEL-402 API Test"
    assert "peptide_candidates" in data
    assert "hla_predictions" in data

    list_resp = await async_client.get("/api/v1/neoantigen-hla-presentation/studies")
    assert list_resp.status_code == 200
    studies = list_resp.json()
    assert len(studies) >= 1