"""Tests for Production Infrastructure REST API endpoints (Phase 24)."""
from uuid import UUID, uuid4
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from api.dependencies import get_current_user, get_optional_current_user
from database.connection import Base
from database.models.user import User as DBUser
from database.repositories.user_repo import UserRepository
from database.repositories.workspace_repo import WorkspaceRepository
from main import app
from shared.auth import User, UserRole, hash_password


@pytest.fixture
async def test_db():
    from database import connection as db_conn

    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    test_session_maker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    orig_engine = db_conn.engine
    orig_maker = db_conn.async_session_maker

    db_conn.engine = test_engine
    db_conn.async_session_maker = test_session_maker

    # Create test user and workspace
    async with test_session_maker() as session:
        user_repo = UserRepository(session)
        alice = DBUser(
            id=UUID("11111111-1111-1111-1111-111111111111"),
            username="alice_admin",
            email="alice@company.com",
            password_hash=hash_password("Pass123!"),
            role=UserRole.ADMIN.value,
            is_active=True,
        )
        await user_repo.create(alice)
        await session.commit()

    yield test_session_maker

    db_conn.engine = orig_engine
    db_conn.async_session_maker = orig_maker
    await test_engine.dispose()


@pytest.fixture
def auth_user():
    return User(
        id="11111111-1111-1111-1111-111111111111",
        username="alice_admin",
        email="alice@company.com",
        role=UserRole.ADMIN,
    )


@pytest.mark.asyncio
async def test_worker_cluster_telemetry_api(test_db, auth_user):
    app.dependency_overrides[get_current_user] = lambda: auth_user
    app.dependency_overrides[get_optional_current_user] = lambda: auth_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Post worker heartbeat
        hb_payload = {
            "worker_id": "worker-eu-central",
            "hostname": "node-eu.cluster.local",
            "concurrency": 6,
            "active_tasks": ["task-101"],
            "cpu_percent": 24.5,
            "memory_mb": 450.0,
            "status": "HEALTHY",
        }
        res = await ac.post("/api/v1/system/workers/heartbeat", json=hb_payload)
        assert res.status_code == 200
        data = res.json()
        assert data["worker_id"] == "worker-eu-central"
        assert data["concurrency"] == 6

        # 2. List workers
        list_res = await ac.get("/api/v1/system/workers")
        assert list_res.status_code == 200
        workers = list_res.json()
        assert len(workers) >= 1

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_task_queue_api(test_db, auth_user):
    app.dependency_overrides[get_current_user] = lambda: auth_user
    app.dependency_overrides[get_optional_current_user] = lambda: auth_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Enqueue task
        task_payload = {
            "task_type": "research_dag",
            "priority": "HIGH",
            "payload": {"query": "Deep Multimodal Fusion"},
        }
        res = await ac.post("/api/v1/system/queue/tasks", json=task_payload)
        assert res.status_code == 201
        task = res.json()
        assert task["task_type"] == "research_dag"
        assert task["priority"] == "HIGH"
        task_id = task["task_id"]

        # 2. Get task status
        get_res = await ac.get(f"/api/v1/system/queue/tasks/{task_id}")
        assert get_res.status_code == 200
        assert get_res.json()["task_id"] == task_id

        # 3. Get queue metrics
        metrics_res = await ac.get("/api/v1/system/queue/status")
        assert metrics_res.status_code == 200
        metrics = metrics_res.json()
        assert metrics["total_tasks"] >= 1

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_object_storage_api(test_db, auth_user):
    app.dependency_overrides[get_current_user] = lambda: auth_user
    app.dependency_overrides[get_optional_current_user] = lambda: auth_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Presigned URL generation
        presigned_res = await ac.post("/api/v1/system/storage/presigned-url", json={
            "object_key": "reports/report-2026.pdf",
            "operation": "get_object",
            "expires_in_seconds": 3600,
        })
        assert presigned_res.status_code == 200
        assert "url" in presigned_res.json()

        # 2. Catalog storage object
        catalog_res = await ac.post("/api/v1/system/storage/objects", json={
            "bucket": "research-artifacts",
            "object_key": "reports/report-2026.pdf",
            "size_bytes": 1048576,  # 1MB
            "etag": '"etag-sample"',
            "md5_hash": "samplemd5hash",
            "sha256_hash": "samplesha256hash",
            "content_type": "application/pdf",
        })
        assert catalog_res.status_code == 201
        assert catalog_res.json()["object_key"] == "reports/report-2026.pdf"

        # 3. List storage objects
        list_res = await ac.get("/api/v1/system/storage/objects")
        assert list_res.status_code == 200
        objects = list_res.json()
        assert len(objects) >= 1

        # 4. Storage usage
        usage_res = await ac.get("/api/v1/system/storage/usage")
        assert usage_res.status_code == 200
        usage = usage_res.json()
        assert "database_catalog_summary" in usage

    app.dependency_overrides.clear()
