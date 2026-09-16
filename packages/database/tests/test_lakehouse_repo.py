"""Unit tests for DataLakeRepository (Phase 52)."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.models.lakehouse import (
    DBDataLakeTable,
    DBDataLakePartition,
    DBSemanticLakeQuery,
)
from database.repositories.lakehouse_repo import DataLakeRepository


@pytest.fixture
async def db_session():
    """Create in-memory SQLite database session for testing."""
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
async def test_lakehouse_repo_lifecycle(db_session: AsyncSession):
    repo = DataLakeRepository(db_session)

    # 1. Create Table
    table = await repo.create_table(
        name="test_genomics_lake",
        modality="GENOMIC",
        storage_format="PARQUET",
        schema_definition={"columns": [{"name": "gene", "type": "VARCHAR"}]},
        description="Genomic test dataset",
        total_records=1000,
        size_bytes=50000,
    )
    assert table.id is not None
    assert table.name == "test_genomics_lake"

    # 2. Get Table
    fetched = await repo.get_table(table.id)
    assert fetched is not None
    assert fetched.modality == "GENOMIC"

    # 3. Add Partition
    partition = await repo.add_partition(
        table_id=table.id,
        partition_key="cohort=BRCA/year=2026",
        record_count=500,
        size_bytes=25000,
        storage_path="s3://lake/test.parquet",
        vector_indexed=True,
    )
    assert partition.id is not None
    assert partition.record_count == 500

    # Verify table aggregates updated
    updated_table = await repo.get_table(table.id)
    assert updated_table.total_records == 1500
    assert updated_table.size_bytes == 75000

    # 4. List Partitions
    partitions = await repo.list_partitions(table.id)
    assert len(partitions) == 1

    # 5. Record Query
    query = await repo.record_query(
        query_text="Find BRCA1 oncogenic variants",
        target_tables=["test_genomics_lake"],
        sql_predicate="p_val < 0.05",
        vector_similarity_threshold=0.80,
        matched_records_count=10,
        execution_time_ms=18.5,
        results_preview=[{"id": 1, "variant": "BRCA1 c.5266dupC"}],
    )
    assert query.id is not None
    assert query.matched_records_count == 10

    # 6. List Queries
    queries = await repo.list_queries()
    assert len(queries) == 1

    # 7. Metrics
    metrics = await repo.get_metrics()
    assert metrics["total_tables"] == 1
    assert metrics["total_partitions"] == 1
    assert metrics["total_records"] == 1500
    assert metrics["total_bytes"] == 75000
    assert metrics["total_queries"] == 1

    # 8. Delete Table
    assert await repo.delete_table(table.id) is True
    assert await repo.get_table(table.id) is None
