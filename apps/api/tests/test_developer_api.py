"""
Tests for Developer Platform & Public REST API endpoints (Phase 25).
"""

from uuid import UUID
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from api.dependencies import get_current_user, get_optional_current_user
from database.connection import Base
from database.models.user import User as DBUser
from database.repositories.user_repo import UserRepository
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

    # Create test user
    async with test_session_maker() as session:
        user_repo = UserRepository(session)
        dev_user = DBUser(
            id=UUID("22222222-2222-2222-2222-222222222222"),
            username="dev_user",
            email="dev@enterprise.ai",
            password_hash=hash_password("DevPass123!"),
            role=UserRole.RESEARCHER.value,
            is_active=True,
        )
        await user_repo.create(dev_user)
        await session.commit()

    yield test_session_maker

    db_conn.engine = orig_engine
    db_conn.async_session_maker = orig_maker
    await test_engine.dispose()


@pytest.fixture
def auth_user():
    return User(
        id="22222222-2222-2222-2222-222222222222",
        username="dev_user",
        email="dev@enterprise.ai",
        role=UserRole.RESEARCHER,
    )


@pytest.mark.asyncio
async def test_developer_key_management_and_public_api(test_db, auth_user):
    app.dependency_overrides[get_current_user] = lambda: auth_user
    app.dependency_overrides[get_optional_current_user] = lambda: auth_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create Developer API Key
        create_res = await client.post(
            "/api/v1/developer/keys",
            json={
                "name": "Integration Test Key",
                "scopes": ["research:read", "research:write", "documents:read", "documents:write"],
                "rate_limit_tier": "pro",
                "expires_in_days": 60,
            },
        )
        assert create_res.status_code == 201
        data = create_res.json()
        assert "secret_key" in data
        assert data["secret_key"].startswith("amrp_live_")
        raw_secret_key = data["secret_key"]
        key_id = data["api_key"]["id"]

        # 2. List API Keys
        list_res = await client.get("/api/v1/developer/keys")
        assert list_res.status_code == 200
        keys_list = list_res.json()
        assert len(keys_list) >= 1
        assert any(k["id"] == key_id for k in keys_list)

        # 3. Access Public Usage Endpoint with X-API-Key
        usage_res = await client.get(
            "/api/v1/developer/usage",
            headers={"X-API-Key": raw_secret_key},
        )
        assert usage_res.status_code == 200
        usage_data = usage_res.json()
        assert usage_data["name"] == "Integration Test Key"
        assert usage_data["tier"] == "pro"
        assert usage_data["rate_limit_rpm"] == 300

        # 4. Trigger Programmatic Research Job
        research_res = await client.post(
            "/api/v1/developer/research",
            headers={"X-API-Key": raw_secret_key},
            json={
                "question": "What is the state of autonomous robotic synthesis in 2026?",
                "routing_profile": "balanced",
                "constraints": ["Cite arXiv references"],
            },
        )
        assert research_res.status_code == 202
        job_data = research_res.json()
        assert "job_id" in job_data
        job_id = job_data["job_id"]

        # 5. Poll Programmatic Research Job
        poll_res = await client.get(
            f"/api/v1/developer/research/{job_id}",
            headers={"X-API-Key": raw_secret_key},
        )
        assert poll_res.status_code == 200
        assert poll_res.json()["job_id"] == job_id

        # 6. Ingest Programmatic Document
        doc_res = await client.post(
            "/api/v1/developer/documents",
            headers={"X-API-Key": raw_secret_key},
            json={
                "title": "Quantum Error Correction 2026",
                "content": "Surface codes have achieved fault-tolerant thresholds below 0.1% physical error rate.",
                "source_type": "text",
            },
        )
        assert doc_res.status_code == 201
        assert "document_id" in doc_res.json()

        # 7. Unauthenticated request should fail with 401
        unauth_res = await client.get("/api/v1/developer/usage")
        assert unauth_res.status_code == 401

        # 8. Revoke API Key
        revoke_res = await client.patch(f"/api/v1/developer/keys/{key_id}/revoke")
        assert revoke_res.status_code == 200

        # 9. Request with revoked key should fail with 401
        revoked_call_res = await client.get(
            "/api/v1/developer/usage",
            headers={"X-API-Key": raw_secret_key},
        )
        assert revoked_call_res.status_code == 401

    app.dependency_overrides.clear()
