"""Tests for Collaboration REST API routes (Phase 19)."""

from uuid import UUID, uuid4
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from api.dependencies import get_current_user, get_optional_current_user
from database.connection import Base
from database.models.report import Report
from database.models.research_job import ResearchJob
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

    # Create test users in DB
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
        bob = DBUser(
            id=UUID("22222222-2222-2222-2222-222222222222"),
            username="bob_analyst",
            email="bob@company.com",
            password_hash=hash_password("Pass123!"),
            role=UserRole.RESEARCHER.value,
            is_active=True,
        )
        await user_repo.create(alice)
        await user_repo.create(bob)
        await session.commit()

    yield test_session_maker

    db_conn.engine = orig_engine
    db_conn.async_session_maker = orig_maker
    await test_engine.dispose()


@pytest.fixture
def alice_user():
    return User(
        id="11111111-1111-1111-1111-111111111111",
        username="alice_admin",
        email="alice@company.com",
        role=UserRole.ADMIN,
        is_active=True,
    )


@pytest.fixture
def bob_user():
    return User(
        id="22222222-2222-2222-2222-222222222222",
        username="bob_analyst",
        email="bob@company.com",
        role=UserRole.RESEARCHER,
        is_active=True,
    )


@pytest.mark.asyncio
async def test_collaboration_invites_and_activities_api(test_db, alice_user, bob_user):
    app.dependency_overrides[get_current_user] = lambda: alice_user
    app.dependency_overrides[get_optional_current_user] = lambda: alice_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Create a workspace as Alice
        ws_res = await client.post("/api/v1/workspaces", json={"name": "Neural Lab"})
        assert ws_res.status_code == 201
        ws_id = ws_res.json()["workspace"]["id"]

        # 2. Alice sends an invite to Bob's email
        inv_res = await client.post(
            f"/api/v1/workspaces/{ws_id}/invites",
            json={"email": "bob@company.com", "role": "researcher"},
        )
        assert inv_res.status_code == 201
        inv_data = inv_res.json()
        token = inv_data["invite"]["token"]
        assert token is not None

        # 3. List invites for workspace
        list_inv = await client.get(f"/api/v1/workspaces/{ws_id}/invites")
        assert list_inv.status_code == 200
        assert list_inv.json()["total"] == 1

        # 4. Inspect invite by token
        token_res = await client.get(f"/api/v1/invites/{token}")
        assert token_res.status_code == 200
        assert token_res.json()["invite"]["email"] == "bob@company.com"

        # 5. Switch auth to Bob and accept invite
        app.dependency_overrides[get_current_user] = lambda: bob_user
        app.dependency_overrides[get_optional_current_user] = lambda: bob_user

        accept_res = await client.post(f"/api/v1/invites/{token}/accept")
        assert accept_res.status_code == 200
        assert accept_res.json()["member"]["user_id"] == bob_user.id

        # 6. Check workspace activities
        act_res = await client.get(f"/api/v1/workspaces/{ws_id}/activities")
        assert act_res.status_code == 200
        acts = act_res.json()["activities"]
        actions = [a["action"] for a in acts]
        assert "member_invited" in actions
        assert "member_joined" in actions

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_report_annotations_api(test_db, alice_user, bob_user):
    app.dependency_overrides[get_current_user] = lambda: bob_user
    app.dependency_overrides[get_optional_current_user] = lambda: bob_user

    # Insert a dummy report into test DB
    report_id = uuid4()
    job_id = uuid4()
    async with test_db() as session:
        job = ResearchJob(
            id=job_id,
            request_id=uuid4(),
            question="GenAI Security Study",
            objective="AI Red Teaming",
            user_id=UUID(alice_user.id),
            status="completed",
        )
        report = Report(
            id=report_id,
            job_id=job_id,
            title="Security Synthesis",
            executive_summary="Findings on prompt injection",
            findings=[{"topic": "Guardrails", "content": "Prompt injection can bypass guardrails without proper sandboxing."}],
        )
        session.add(job)
        session.add(report)
        await session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Bob posts an annotation
        ann_res = await client.post(
            f"/api/v1/reports/{report_id}/annotations",
            json={
                "comment_text": "Verify whether NeMo guardrails were tested.",
                "section_index": 0,
                "selected_text": "Prompt injection can bypass guardrails",
            },
        )
        assert ann_res.status_code == 201
        ann_id = ann_res.json()["annotation"]["id"]
        assert ann_res.json()["annotation"]["status"] == "open"

        # 2. List annotations for report
        list_res = await client.get(f"/api/v1/reports/{report_id}/annotations")
        assert list_res.status_code == 200
        assert list_res.json()["total"] == 1

        # 3. Resolve annotation
        res_res = await client.patch(f"/api/v1/annotations/{ann_id}/resolve")
        assert res_res.status_code == 200
        assert res_res.json()["annotation"]["status"] == "resolved"

        # 4. Delete annotation
        del_res = await client.delete(f"/api/v1/annotations/{ann_id}")
        assert del_res.status_code == 200
        assert del_res.json()["success"] is True

        # Verify list is empty
        empty_res = await client.get(f"/api/v1/reports/{report_id}/annotations")
        assert empty_res.json()["total"] == 0

    app.dependency_overrides.clear()
