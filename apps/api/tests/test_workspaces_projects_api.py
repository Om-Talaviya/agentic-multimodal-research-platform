"""Tests for Workspaces and Projects REST API routes (Phase 18)."""

from uuid import UUID
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from main import app
from database.connection import Base, get_db_session
from database.models.user import User as DBUser
from database.repositories.user_repo import UserRepository
from api.dependencies import get_current_user, get_optional_current_user
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
            username="test_researcher",
            email="researcher@test.ai",
            password_hash=hash_password("Pass123!"),
            role=UserRole.RESEARCHER.value,
            is_active=True,
        )
        await user_repo.create(db_user)
        await session.commit()

    async def override_get_db():
        async with test_session_maker() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_get_db

    yield test_session_maker

    app.dependency_overrides.pop(get_db_session, None)
    db_conn.engine = orig_engine
    db_conn.async_session_maker = orig_maker
    await test_engine.dispose()


@pytest.fixture
def sample_user():
    return User(
        id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        username="test_researcher",
        email="researcher@test.ai",
        role=UserRole.RESEARCHER,
        is_active=True,
    )


@pytest.mark.asyncio
async def test_workspaces_and_projects_full_lifecycle(test_db, sample_user):
    app.dependency_overrides[get_current_user] = lambda: sample_user
    app.dependency_overrides[get_optional_current_user] = lambda: sample_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Create a workspace
        resp = await client.post(
            "/api/v1/workspaces",
            json={
                "name": "Genomics Lab",
                "description": "Genomic sequencing & AI analysis",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["success"] is True
        ws_id = data["workspace"]["id"]
        assert data["workspace"]["name"] == "Genomics Lab"
        assert data["workspace"]["slug"] == "genomics-lab"

        # 2. List workspaces
        list_resp = await client.get("/api/v1/workspaces")
        assert list_resp.status_code == 200
        list_data = list_resp.json()
        assert list_data["total"] >= 1
        assert any(w["id"] == ws_id for w in list_data["workspaces"])

        # 3. Get workspace details and members
        detail_resp = await client.get(f"/api/v1/workspaces/{ws_id}")
        assert detail_resp.status_code == 200
        detail_data = detail_resp.json()
        assert detail_data["workspace"]["name"] == "Genomics Lab"
        assert detail_data["user_role"] == "owner"
        assert len(detail_data["members"]) == 1

        # 4. Workspace projects list (auto-provisioned 'General Research')
        proj_list_resp = await client.get(f"/api/v1/workspaces/{ws_id}/projects")
        assert proj_list_resp.status_code == 200
        proj_list = proj_list_resp.json()
        assert proj_list["total"] == 1
        assert proj_list["projects"][0]["name"] == "General Research"

        # 5. Create a new custom project
        create_proj_resp = await client.post(
            f"/api/v1/workspaces/{ws_id}/projects",
            json={
                "name": "Target Validation",
                "description": "Oncology target discovery",
            },
        )
        assert create_proj_resp.status_code == 201
        created_proj = create_proj_resp.json()
        proj_id = created_proj["project"]["id"]
        assert created_proj["project"]["name"] == "Target Validation"

        # 6. Fetch project details and overview metrics
        proj_resp = await client.get(f"/api/v1/projects/{proj_id}")
        assert proj_resp.status_code == 200
        assert proj_resp.json()["project"]["name"] == "Target Validation"

        overview_resp = await client.get(f"/api/v1/projects/{proj_id}/overview")
        assert overview_resp.status_code == 200
        overview_data = overview_resp.json()
        assert "metrics" in overview_data
        assert overview_data["metrics"]["total_jobs"] == 0

        # 7. Update project
        update_resp = await client.patch(
            f"/api/v1/projects/{proj_id}",
            json={"description": "Updated oncology research"},
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["project"]["description"] == "Updated oncology research"

        # 8. Delete project
        del_resp = await client.delete(f"/api/v1/projects/{proj_id}")
        assert del_resp.status_code == 200
        assert del_resp.json()["success"] is True

    app.dependency_overrides.clear()
