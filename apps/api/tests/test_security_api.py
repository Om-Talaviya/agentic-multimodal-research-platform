"""Tests for Enterprise Security REST API routes (Phase 23)."""
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

        ws_repo = WorkspaceRepository(session)
        ws = await ws_repo.create_workspace(
            name="Security Workspace",
            description="Enterprise Test Workspace",
            owner_id=alice.id,
        )
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
async def test_security_audit_logs_and_verification_api(test_db, auth_user):
    app.dependency_overrides[get_current_user] = lambda: auth_user
    app.dependency_overrides[get_optional_current_user] = lambda: auth_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Post audit log
        log_payload = {
            "event_type": "user.login",
            "action": "session_authenticate",
            "severity": "INFO",
            "details": {"ip": "10.0.0.1"},
        }
        res = await ac.post("/api/v1/security/audit-logs", json=log_payload)
        assert res.status_code == 201
        data = res.json()
        assert data["event_type"] == "user.login"
        assert data["previous_hash"] is not None
        assert data["current_hash"] is not None

        # 2. List audit logs
        list_res = await ac.get("/api/v1/security/audit-logs")
        assert list_res.status_code == 200
        logs = list_res.json()
        assert len(logs) >= 1

        # 3. Verify cryptographic hash chain
        verify_res = await ac.get("/api/v1/security/audit-logs/verify")
        assert verify_res.status_code == 200
        verify_data = verify_res.json()
        assert verify_data["verified"] is True
        assert verify_data["integrity_status"] == "VALID_TAMPER_EVIDENT"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_kms_secret_vault_api(test_db, auth_user):
    app.dependency_overrides[get_current_user] = lambda: auth_user
    app.dependency_overrides[get_optional_current_user] = lambda: auth_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Store secret
        secret_payload = {
            "name": "Gemini Production Key",
            "secret_type": "api_key",
            "provider": "gemini",
            "plaintext_value": "AIzaSy_SecretTestAPIKey998877",
        }
        res = await ac.post("/api/v1/security/secrets", json=secret_payload)
        assert res.status_code == 201
        secret = res.json()
        assert secret["name"] == "Gemini Production Key"
        assert "AIz" in secret["masked_preview"]
        secret_id = secret["id"]

        # 2. List secrets (plaintext should not be exposed)
        list_res = await ac.get("/api/v1/security/secrets")
        assert list_res.status_code == 200
        secrets = list_res.json()
        assert len(secrets) >= 1
        assert "plaintext_value" not in secrets[0]

        # 3. Revoke secret
        revoke_res = await ac.patch(f"/api/v1/security/secrets/{secret_id}/revoke")
        assert revoke_res.status_code == 200
        assert revoke_res.json()["status"] == "REVOKED"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_compliance_and_gdpr_purge_api(test_db, auth_user):
    app.dependency_overrides[get_current_user] = lambda: auth_user
    app.dependency_overrides[get_optional_current_user] = lambda: auth_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Get compliance status
        comp_res = await ac.get("/api/v1/security/compliance/status")
        assert comp_res.status_code == 200
        comp_data = comp_res.json()
        assert comp_data["soc2_compliance"]["status"] == "COMPLIANT"
        assert comp_data["gdpr_compliance"]["status"] == "COMPLIANT"

        # 2. Test GDPR purge invalid confirmation code
        ws_id = str(uuid4())
        bad_purge = await ac.post("/api/v1/security/gdpr/purge", json={
            "workspace_id": ws_id,
            "confirmation_code": "WRONG_CODE"
        })
        assert bad_purge.status_code == 400

        # 3. Test GDPR purge valid confirmation code
        good_purge = await ac.post("/api/v1/security/gdpr/purge", json={
            "workspace_id": ws_id,
            "confirmation_code": "CONFIRM_GDPR_PURGE"
        })
        assert good_purge.status_code == 200
        assert good_purge.json()["status"] == "COMPLETED_GDPR_PURGE"

    app.dependency_overrides.clear()
