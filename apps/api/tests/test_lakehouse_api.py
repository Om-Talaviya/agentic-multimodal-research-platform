"""Integration tests for Scientific Lakehouse REST API (Phase 52)."""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from api.dependencies import get_db_session
from database.connection import Base
from main import app


@pytest.fixture
async def async_test_session():
    """Create in-memory SQLite database session for API integration tests."""
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
async def test_lakehouse_api_full_workflow(async_test_session: AsyncSession):
    async def override_get_db():
        yield async_test_session

    app.dependency_overrides[get_db_session] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Register Table
        tbl_payload = {
            "name": "tcga_luad_rnaseq_test",
            "modality": "GENOMIC",
            "storage_format": "PARQUET",
            "description": "TCGA Lung Adenocarcinoma Single-Cell Matrix",
            "total_records": 10000,
            "size_bytes": 104857600
        }
        res = await client.post("/api/v1/lakehouse/tables", json=tbl_payload)
        assert res.status_code == 201
        data = res.json()
        assert data["name"] == "tcga_luad_rnaseq_test"
        table_id = data["id"]

        # 2. Add Partition
        part_payload = {
            "partition_key": "cohort=LUAD_2026/stage=IV",
            "record_count": 5000,
            "size_bytes": 52428800,
            "storage_path": "s3://lakehouse/genomics/tcga_luad_part1.parquet",
            "vector_indexed": True
        }
        part_res = await client.post(f"/api/v1/lakehouse/tables/{table_id}/partitions", json=part_payload)
        assert part_res.status_code == 201
        assert part_res.json()["partition_key"] == "cohort=LUAD_2026/stage=IV"

        # 3. Get Table Details
        get_res = await client.get(f"/api/v1/lakehouse/tables/{table_id}")
        assert get_res.status_code == 200
        tbl_detail = get_res.json()
        assert len(tbl_detail["partitions"]) == 1
        assert tbl_detail["total_records"] == 15000

        # 4. List Tables
        list_res = await client.get("/api/v1/lakehouse/tables")
        assert list_res.status_code == 200
        tables = list_res.json()
        assert any(t["id"] == table_id for t in tables)

        # 5. Execute Semantic Query
        query_payload = {
            "query_text": "Find EGFR exon 20 insertions with resistance biomarkers",
            "target_tables": ["tcga_luad_rnaseq_test"],
            "sql_predicate": "significance_pvalue < 0.01",
            "vector_similarity_threshold": 0.75,
            "limit": 5
        }
        q_res = await client.post("/api/v1/lakehouse/query", json=query_payload)
        assert q_res.status_code == 200
        q_data = q_res.json()
        assert q_data["matched_records_count"] > 0
        assert len(q_data["results"]) > 0

        # 6. List Queries
        queries_res = await client.get("/api/v1/lakehouse/queries")
        assert queries_res.status_code == 200
        assert len(queries_res.json()) >= 1

        # 7. Get Metrics
        m_res = await client.get("/api/v1/lakehouse/metrics")
        assert m_res.status_code == 200
        metrics = m_res.json()
        assert metrics["total_tables"] >= 1
        assert metrics["total_partitions"] >= 1
        assert metrics["total_queries"] >= 1

        # 8. Delete Table
        del_res = await client.delete(f"/api/v1/lakehouse/tables/{table_id}")
        assert del_res.status_code == 200
