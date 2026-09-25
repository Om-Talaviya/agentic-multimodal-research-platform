"""Tests for Phase 181: Rare Disease Deep Phenotyping API."""

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
async def test_rare_disease_hpo_endpoint(async_client: AsyncClient):
    payload = {
        "name": "Patient RD-8841 Analysis API Test",
        "patient_cohort_id": "PT-RD-8841",
        "clinical_narrative": "Tall stature, arachnodactyly, aortic root aneurysm, mitral valve prolapse, ectopia lentis",
    }

    response = await async_client.post("/api/v1/rare-disease-hpo-phenotyping/analyze", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Patient RD-8841 Analysis API Test"
    assert "extracted_hpo_terms" in data
    assert "ranked_omim_matches" in data

    list_resp = await async_client.get("/api/v1/rare-disease-hpo-phenotyping/studies")
    assert list_resp.status_code == 200
    studies = list_resp.json()
    assert len(studies) >= 1