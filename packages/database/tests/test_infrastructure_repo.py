"""Database repository tests for InfrastructureRepository (Phase 24)."""
import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.models.infrastructure import DBStorageObject, DBWorkerNode
from database.repositories.infrastructure_repo import InfrastructureRepository

@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_factory() as session:
        yield session
    await engine.dispose()

@pytest.mark.asyncio
async def test_worker_node_registration_and_sweep(async_session: AsyncSession):
    repo = InfrastructureRepository(async_session)

    # Register worker
    w1 = await repo.register_or_heartbeat_worker(
        worker_id="node-us-east-1",
        hostname="east-1.internal",
        concurrency=8,
        active_tasks=["task-001", "task-002"],
        cpu_percent=32.0,
        memory_mb=1024.0,
        status="HEALTHY",
    )
    assert w1.worker_id == "node-us-east-1"
    assert w1.concurrency == 8
    assert len(w1.active_tasks) == 2

    # List workers
    workers = await repo.list_workers()
    assert len(workers) == 1
    assert workers[0].worker_id == "node-us-east-1"

    # Heartbeat update
    w1_updated = await repo.register_or_heartbeat_worker(
        worker_id="node-us-east-1",
        active_tasks=[],
        cpu_percent=10.0,
        memory_mb=512.0,
    )
    assert len(w1_updated.active_tasks) == 0
    assert w1_updated.cpu_percent == 10.0

@pytest.mark.asyncio
async def test_storage_object_catalog_and_usage(async_session: AsyncSession):
    repo = InfrastructureRepository(async_session)
    ws_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Record storage object
    obj1 = await repo.record_storage_object(
        bucket="research-artifacts",
        object_key="reports/summary.pdf",
        size_bytes=204800,  # 200 KB
        etag='"etag123"',
        md5_hash="md5hash123",
        sha256_hash="sha256hash123",
        content_type="application/pdf",
        workspace_id=ws_id,
        uploader_id=user_id,
    )
    assert obj1.object_key == "reports/summary.pdf"
    assert obj1.size_bytes == 204800

    # Record second object
    obj2 = await repo.record_storage_object(
        bucket="research-artifacts",
        object_key="datasets/data.csv",
        size_bytes=512000,  # 500 KB
        etag='"etag456"',
        md5_hash="md5hash456",
        sha256_hash="sha256hash456",
        content_type="text/csv",
        workspace_id=ws_id,
        uploader_id=user_id,
    )

    # Query list
    objects = await repo.list_storage_objects(workspace_id=ws_id)
    assert len(objects) == 2

    # Usage summary
    summary = await repo.get_storage_usage_summary(workspace_id=ws_id)
    assert summary["total_objects"] == 2
    assert summary["total_bytes"] == 716800
    assert summary["total_mb"] == round(716800 / (1024 * 1024), 2)
