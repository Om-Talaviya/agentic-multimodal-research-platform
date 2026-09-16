"""
Integration tests for Epigenomics REST API (Phase 56).
"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from api.dependencies import get_db_session
from database.connection import Base
from main import app


@pytest.fixture
async def async_test_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_epigenomics_api_full_workflow(async_test_session: AsyncSession):
    async def override_get_db():
        yield async_test_session

    app.dependency_overrides[get_db_session] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create Experiment
        res = await client.post(
            "/api/v1/epigenomics/experiments",
            json={
                "sample_id": "SAM-ATAC-TEST-02",
                "tissue_type": "Glioblastoma",
                "assay_type": "ATAC-seq",
                "sequencing_depth_millions": 60.0,
                "target_genes": ["EGFR", "SOX2"],
            },
        )
        assert res.status_code == 201
        data = res.json()
        exp_id = data["id"]
        assert len(data["peaks"]) == 2

        # 2. Get Experiment Detail
        get_res = await client.get(f"/api/v1/epigenomics/experiments/{exp_id}")
        assert get_res.status_code == 200
        assert get_res.json()["sample_id"] == "SAM-ATAC-TEST-02"

        # 3. List Experiments
        list_res = await client.get("/api/v1/epigenomics/experiments")
        assert list_res.status_code == 200
        assert any(e["id"] == exp_id for e in list_res.json())

        # 4. Filter Peaks
        peaks_res = await client.get(f"/api/v1/epigenomics/experiments/{exp_id}/peaks")
        assert peaks_res.status_code == 200
        assert len(peaks_res.json()) == 2
