"""
API integration tests for Phase 128: CITE-seq Multi-Modal Endpoints.
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
async def test_citeseq_api_flow(test_app: AsyncClient):
    payload = {
        "sample_name": "Glioblastoma_CITEseq_54P",
        "tissue_origin": "Primary Brain Tumor",
    }

    # 1. Analyze CITE-seq
    res = await test_app.post("/api/v1/citeseq/analyze", json=payload)
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["status"] == "success"
    assert "dataset_id" in data
    dataset_id = data["dataset_id"]
    assert data["antibodies_count"] >= 4
    assert data["expressions_count"] >= 6

    # 2. List datasets
    list_res = await test_app.get("/api/v1/citeseq/datasets")
    assert list_res.status_code == 200
    datasets = list_res.json()
    assert any(d["id"] == dataset_id for d in datasets)

    # 3. Retrieve single dataset
    get_res = await test_app.get(f"/api/v1/citeseq/datasets/{dataset_id}")
    assert get_res.status_code == 200
    detail = get_res.json()
    assert detail["sample_name"] == "Glioblastoma_CITEseq_54P"
    assert len(detail["antibodies"]) >= 4
    assert len(detail["expressions"]) >= 6
