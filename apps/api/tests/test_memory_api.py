"""Tests for Research Memory API routes (Phase 16)."""

from uuid import uuid4, UUID
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from main import app
from database.connection import Base, get_db_session
from database.models.user import User as DBUser
from database.repositories.user_repo import UserRepository
from api.dependencies import get_current_user, get_optional_current_user, get_memory_manager
from research.memory.manager import ResearchMemoryManager
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

    # Create test user in DB
    async with test_session_maker() as session:
        user_repo = UserRepository(session)
        db_user = DBUser(
            id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            username="memory_researcher",
            email="researcher@platform.ai",
            password_hash=hash_password("StrongPass123!"),
            role=UserRole.RESEARCHER.value,
            is_active=True,
        )
        await user_repo.create(db_user)
        await session.commit()

    yield test_session_maker

    db_conn.engine = orig_engine
    db_conn.async_session_maker = orig_maker
    await test_engine.dispose()


@pytest.fixture
def sample_user():
    return User(
        id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        username="memory_researcher",
        email="researcher@platform.ai",
        role=UserRole.RESEARCHER,
        is_active=True,
    )


@pytest.mark.asyncio
async def test_memory_crud_api_lifecycle(test_db, sample_user):
    async def override_get_session():
        async with test_db() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_session] = override_get_session
    app.dependency_overrides[get_current_user] = lambda: sample_user
    app.dependency_overrides[get_optional_current_user] = lambda: sample_user

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. Create a memory
            create_payload = {
                "title": "Scaling Laws for Neural Language Models",
                "content": "Cross-entropy loss scales as a power-law with compute, dataset size, and parameter count.",
                "memory_type": "finding",
                "tags": ["scaling", "compute", "transformers"],
                "confidence": 0.96,
                "metadata": {"source_paper": "Kaplan et al., 2020"},
            }
            create_resp = await client.post("/api/v1/memory", json=create_payload)
            assert create_resp.status_code == 201
            created_data = create_resp.json()
            assert created_data["title"] == "Scaling Laws for Neural Language Models"
            assert created_data["memory_type"] == "finding"
            memory_id = created_data["id"]

            # 2. List memories
            list_resp = await client.get("/api/v1/memory")
            assert list_resp.status_code == 200
            list_data = list_resp.json()
            assert isinstance(list_data, list)
            assert any(m["id"] == memory_id for m in list_data)

            # 3. Get specific memory
            get_resp = await client.get(f"/api/v1/memory/{memory_id}")
            assert get_resp.status_code == 200
            assert get_resp.json()["id"] == memory_id

            # 4. Search / recall memories
            search_resp = await client.get(
                "/api/v1/memory/search",
                params={"query": "power-law cross-entropy compute"},
            )
            assert search_resp.status_code == 200
            search_data = search_resp.json()
            assert "memories" in search_data
            assert len(search_data["memories"]) >= 1

            # 5. Patch / update memory
            patch_resp = await client.patch(
                f"/api/v1/memory/{memory_id}",
                json={"title": "Updated Scaling Laws Title", "confidence": 0.99},
            )
            assert patch_resp.status_code == 200
            assert patch_resp.json()["title"] == "Updated Scaling Laws Title"
            assert patch_resp.json()["confidence"] == 0.99

            # 6. Delete memory
            del_resp = await client.delete(f"/api/v1/memory/{memory_id}")
            assert del_resp.status_code == 204

            # Verify deletion
            get_after_del = await client.get(f"/api/v1/memory/{memory_id}")
            assert get_after_del.status_code == 404
    finally:
        app.dependency_overrides.clear()
