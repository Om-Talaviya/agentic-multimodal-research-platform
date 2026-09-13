"""Tests for WorkspaceInviteRepository, ReportAnnotationRepository, and WorkspaceActivityRepository."""

from datetime import UTC, datetime, timedelta
import uuid
from uuid import uuid4
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.connection import Base
from database.models.collaboration import DBReportAnnotation, DBWorkspaceActivity, DBWorkspaceInvite
from database.models.report import Report
from database.models.research_job import ResearchJob
from database.models.user import User as DBUser
from database.repositories.collaboration_repo import (
    ReportAnnotationRepository,
    WorkspaceActivityRepository,
    WorkspaceInviteRepository,
)
from database.repositories.user_repo import UserRepository
from database.repositories.workspace_repo import WorkspaceRepository
from shared.auth import UserRole, hash_password


@pytest_asyncio.fixture
async def async_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def alice(async_db: AsyncSession) -> DBUser:
    user_repo = UserRepository(async_db)
    user = DBUser(
        username="alice",
        email="alice@example.com",
        password_hash=hash_password("SecurePass123!"),
        role=UserRole.ADMIN.value,
        is_active=True,
    )
    created = await user_repo.create(user)
    await async_db.commit()
    return created


@pytest_asyncio.fixture
async def bob(async_db: AsyncSession) -> DBUser:
    user_repo = UserRepository(async_db)
    user = DBUser(
        username="bob",
        email="bob@example.com",
        password_hash=hash_password("SecurePass123!"),
        role=UserRole.RESEARCHER.value,
        is_active=True,
    )
    created = await user_repo.create(user)
    await async_db.commit()
    return created


@pytest.mark.asyncio
async def test_workspace_invites_flow(async_db: AsyncSession, alice: DBUser, bob: DBUser):
    ws_repo = WorkspaceRepository(async_db)
    invite_repo = WorkspaceInviteRepository(async_db)

    # 1. Alice creates workspace
    ws = await ws_repo.create_workspace("Quantum Lab", owner_id=alice.id)
    await async_db.commit()

    # 2. Alice invites Bob
    invite = await invite_repo.create_invite(
        workspace_id=ws.id,
        email="bob@example.com",
        role="reviewer",
        invited_by=alice.id,
    )
    await async_db.commit()

    assert invite.token is not None
    assert invite.is_accepted is False
    assert invite.role == "reviewer"

    # 3. List invites for workspace
    invites = await invite_repo.list_for_workspace(ws.id)
    assert len(invites) == 1
    assert invites[0].email == "bob@example.com"

    # 4. Fetch invite by token
    fetched = await invite_repo.get_by_token(invite.token)
    assert fetched is not None
    assert fetched.id == invite.id

    # 5. Bob accepts invite
    member = await invite_repo.accept_invite(invite.token, bob.id)
    await async_db.commit()

    assert member is not None
    assert member.role == "reviewer"
    assert member.user_id == bob.id
    assert member.workspace_id == ws.id

    # 6. Verify invite is now accepted
    updated_invite = await invite_repo.get_by_token(invite.token)
    assert updated_invite.is_accepted is True

    # 7. Second accept attempt returns None
    second_accept = await invite_repo.accept_invite(invite.token, bob.id)
    assert second_accept is None


@pytest.mark.asyncio
async def test_workspace_invite_revocation(async_db: AsyncSession, alice: DBUser):
    ws_repo = WorkspaceRepository(async_db)
    invite_repo = WorkspaceInviteRepository(async_db)

    ws = await ws_repo.create_workspace("AI Research Hub", owner_id=alice.id)
    invite = await invite_repo.create_invite(
        workspace_id=ws.id,
        email="carol@example.com",
        role="analyst",
        invited_by=alice.id,
    )
    await async_db.commit()

    # Revoke
    revoked = await invite_repo.revoke_invite(invite.id)
    await async_db.commit()
    assert revoked is True

    # Verify not found
    fetched = await invite_repo.get_by_id(invite.id)
    assert fetched is None


@pytest.mark.asyncio
async def test_report_annotations_flow(async_db: AsyncSession, alice: DBUser, bob: DBUser):
    annotation_repo = ReportAnnotationRepository(async_db)

    # Setup a dummy job and report
    job = ResearchJob(
        request_id=uuid4(),
        question="What are recent High Tc Superconductors findings?",
        objective="Analyze superconductor research",
        user_id=alice.id,
        status="completed",
    )
    async_db.add(job)
    await async_db.flush()

    report = Report(
        job_id=job.id,
        title="Superconductor Findings Report",
        executive_summary="Room temperature superconductivity remains unconfirmed in ambient conditions.",
        findings=[{"topic": "Resistance Drop", "content": "Superconductivity requires cryogenic cooling."}],
    )
    async_db.add(report)
    await async_db.flush()
    await async_db.commit()

    # 1. Bob comments on report
    ann1 = await annotation_repo.create_annotation(
        report_id=report.id,
        user_id=bob.id,
        comment_text="We need to verify the Meissner effect resistance drop threshold.",
        section_index=1,
        selected_text="Room temperature superconductivity",
    )
    await async_db.commit()

    assert ann1.id is not None
    assert ann1.status == "open"
    assert ann1.selected_text == "Room temperature superconductivity"

    # 2. List annotations
    annotations = await annotation_repo.list_for_report(report.id)
    assert len(annotations) == 1
    assert annotations[0].comment_text.startswith("We need to verify")

    # 3. Alice resolves the comment
    resolved = await annotation_repo.resolve_annotation(ann1.id, resolved_by=alice.id)
    await async_db.commit()

    assert resolved is not None
    assert resolved.status == "resolved"
    assert resolved.resolved_by == alice.id
    assert resolved.resolved_at is not None

    # 4. Filter by status
    open_anns = await annotation_repo.list_for_report(report.id, status="open")
    assert len(open_anns) == 0

    resolved_anns = await annotation_repo.list_for_report(report.id, status="resolved")
    assert len(resolved_anns) == 1

    # 5. Delete annotation
    deleted = await annotation_repo.delete_annotation(ann1.id)
    await async_db.commit()
    assert deleted is True

    remaining = await annotation_repo.list_for_report(report.id)
    assert len(remaining) == 0


@pytest.mark.asyncio
async def test_workspace_activities_flow(async_db: AsyncSession, alice: DBUser, bob: DBUser):
    ws_repo = WorkspaceRepository(async_db)
    activity_repo = WorkspaceActivityRepository(async_db)

    ws = await ws_repo.create_workspace("Robotics Lab", owner_id=alice.id)
    proj_id = uuid4()
    await async_db.commit()

    # 1. Log activities
    await activity_repo.log_activity(
        workspace_id=ws.id,
        action="workspace_created",
        user_id=alice.id,
        details={"name": ws.name},
    )
    await activity_repo.log_activity(
        workspace_id=ws.id,
        action="project_created",
        user_id=alice.id,
        project_id=proj_id,
        details={"name": "Locomotion Models"},
    )
    await activity_repo.log_activity(
        workspace_id=ws.id,
        action="member_joined",
        user_id=bob.id,
        details={"role": "researcher"},
    )
    await async_db.commit()

    # 2. List for workspace
    activities = await activity_repo.list_for_workspace(ws.id, limit=10)
    assert len(activities) == 3
    # Ordered desc by created_at
    assert activities[0].action == "member_joined"
    assert activities[1].action == "project_created"
    assert activities[2].action == "workspace_created"

    # 3. List for specific project
    proj_acts = await activity_repo.list_for_project(proj_id)
    assert len(proj_acts) == 1
    assert proj_acts[0].action == "project_created"
