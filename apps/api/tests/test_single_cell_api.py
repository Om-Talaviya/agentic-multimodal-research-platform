"""Integration tests for Autonomous Multi-Omics & Single-Cell Transcriptomics API (Phase 41)."""

import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from api.dependencies import get_current_user, get_db_session
from database.connection import Base
from database.models.user import User as DBUser
from main import app


@pytest.fixture
async def async_test_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def mock_user():
    return DBUser(
        id=uuid.uuid4(),
        username="single_cell_lead",
        email="scrna_lead@broadinstitute.org",
        password_hash="mocked",
        role="Researcher",
    )


@pytest.mark.asyncio
async def test_single_cell_api_workflow(async_test_session: AsyncSession, mock_user: DBUser):
    async_test_session.add(mock_user)
    await async_test_session.commit()

    async def override_get_db():
        yield async_test_session

    async def override_get_user():
        return mock_user

    app.dependency_overrides[get_db_session] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. POST /api/v1/single-cell/analyze
        payload = {
            "dataset_title": "Human Liver Hepatocytes & LNP Uptake Atlas",
            "tissue": "Liver",
            "organism": "Homo sapiens",
            "sequencing_platform": "10x Chromium Next GEM 3' v3.1",
            "clustering_resolution": 0.5,
            "total_cells": 300,
        }
        res = await client.post("/api/v1/single-cell/analyze", json=payload)
        assert res.status_code == 201
        data = res.json()
        assert data["dataset_title"] == "Human Liver Hepatocytes & LNP Uptake Atlas"
        assert data["clusters_count"] > 0
        dataset_id = data["dataset_id"]

        # 2. GET /api/v1/single-cell/datasets
        res = await client.get("/api/v1/single-cell/datasets")
        assert res.status_code == 200
        assert res.json()["count"] >= 1

        # 3. GET /api/v1/single-cell/datasets/{id}
        res = await client.get(f"/api/v1/single-cell/datasets/{dataset_id}")
        assert res.status_code == 200
        detail = res.json()
        assert detail["id"] == dataset_id
        assert len(detail["clusters"]) > 0
        assert len(detail["differential_genes"]) > 0
        assert len(detail["pathway_enrichments"]) > 0

        # 4. GET /api/v1/single-cell/datasets/{id}/coordinates
        res = await client.get(f"/api/v1/single-cell/datasets/{dataset_id}/coordinates?limit=100")
        assert res.status_code == 200
        coords_data = res.json()
        assert len(coords_data["coordinates"]) > 0
        assert "umap_x" in coords_data["coordinates"][0]

        # 5. GET /api/v1/single-cell/datasets/{id}/markers
        res = await client.get(f"/api/v1/single-cell/datasets/{dataset_id}/markers?cluster_index=0")
        assert res.status_code == 200
        markers_data = res.json()
        assert markers_data["count"] > 0

        # 6. DELETE /api/v1/single-cell/datasets/{id}
        res = await client.delete(f"/api/v1/single-cell/datasets/{dataset_id}")
        assert res.status_code == 200
        assert res.json()["status"] == "deleted"

    app.dependency_overrides.clear()
