"""Tests for WorkspaceRepository, ProjectRepository, and workspace scoping."""

import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.models.user import User as DBUser
from database.models.research_job import ResearchJob
from database.models.document import Document
from database.models.memory import DBResearchMemory
from database.models.graph import DBKnowledgeEntity
from database.repositories.workspace_repo import WorkspaceRepository
from database.repositories.project_repo import ProjectRepository
from database.repositories.user_repo import UserRepository
from shared.auth import hash_password, UserRole


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
async def sample_user(async_db: AsyncSession) -> DBUser:
    user_repo = UserRepository(async_db)
    user = DBUser(
        username="alice",
        email="alice@example.com",
        password_hash=hash_password("SecurePassword123!"),
        role=UserRole.RESEARCHER.value,
        is_active=True,
    )
    created = await user_repo.create(user)
    await async_db.commit()
    return created


@pytest_asyncio.fixture
async def sample_user_bob(async_db: AsyncSession) -> DBUser:
    user_repo = UserRepository(async_db)
    user = DBUser(
        username="bob",
        email="bob@example.com",
        password_hash=hash_password("SecurePassword123!"),
        role=UserRole.RESEARCHER.value,
        is_active=True,
    )
    created = await user_repo.create(user)
    await async_db.commit()
    return created


@pytest.mark.asyncio
async def test_workspace_creation_and_membership(async_db: AsyncSession, sample_user: DBUser, sample_user_bob: DBUser):
    ws_repo = WorkspaceRepository(async_db)

    # 1. Create workspace
    workspace = await ws_repo.create_workspace(
        name="Quantum Labs",
        owner_id=sample_user.id,
        description="Quantum computing research lab",
    )
    assert workspace.id is not None
    assert workspace.name == "Quantum Labs"
    assert workspace.slug == "quantum-labs"
    assert workspace.owner_id == sample_user.id

    # 2. Verify creator is automatically registered as owner member
    members = await ws_repo.get_members(workspace.id)
    assert len(members) == 1
    assert members[0].user_id == sample_user.id
    assert members[0].role == "owner"

    # 3. Add Bob as a researcher
    member_bob = await ws_repo.add_member(workspace.id, sample_user_bob.id, role="researcher")
    assert member_bob.role == "researcher"

    members_updated = await ws_repo.get_members(workspace.id)
    assert len(members_updated) == 2

    # 4. List workspaces for users
    alice_workspaces = await ws_repo.list_for_user(sample_user.id)
    assert len(alice_workspaces) == 1
    assert alice_workspaces[0].slug == "quantum-labs"

    bob_workspaces = await ws_repo.list_for_user(sample_user_bob.id)
    assert len(bob_workspaces) == 1
    assert bob_workspaces[0].id == workspace.id


@pytest.mark.asyncio
async def test_workspace_slug_collision_handling(async_db: AsyncSession, sample_user: DBUser):
    ws_repo = WorkspaceRepository(async_db)

    ws1 = await ws_repo.create_workspace(name="AI Research", owner_id=sample_user.id)
    ws2 = await ws_repo.create_workspace(name="AI Research", owner_id=sample_user.id)

    assert ws1.slug == "ai-research"
    assert ws2.slug == "ai-research-1"


@pytest.mark.asyncio
async def test_project_crud_and_overview(async_db: AsyncSession, sample_user: DBUser):
    ws_repo = WorkspaceRepository(async_db)
    proj_repo = ProjectRepository(async_db)

    workspace = await ws_repo.create_workspace(name="BioTech Workspace", owner_id=sample_user.id)

    # 1. Create project
    project = await proj_repo.create_project(
        workspace_id=workspace.id,
        name="CRISPR Therapeutics",
        created_by=sample_user.id,
        description="Gene editing literature review",
    )
    assert project.id is not None
    assert project.name == "CRISPR Therapeutics"
    assert project.slug == "crispr-therapeutics"

    # 2. Add sample entities linked to this project
    job = ResearchJob(
        request_id=uuid4(),
        user_id=sample_user.id,
        workspace_id=workspace.id,
        project_id=project.id,
        question="How does Cas9 function?",
        objective="Analyze mechanism",
        status="completed",
    )
    doc = Document(
        user_id=sample_user.id,
        workspace_id=workspace.id,
        project_id=project.id,
        filename="crispr_paper.pdf",
        mime_type="application/pdf",
        file_size=1024,
    )
    mem = DBResearchMemory(
        user_id=sample_user.id,
        project_id=str(project.id),
        title="Cas9 PAM Site Requirement",
        content="Cas9 requires 5'-NGG PAM site for DNA cleavage.",
    )
    entity = DBKnowledgeEntity(
        user_id=sample_user.id,
        workspace_id=workspace.id,
        project_id=project.id,
        name="CRISPR-Cas9",
        canonical_name="crispr-cas9",
        entity_type="TECHNOLOGY",
    )

    async_db.add_all([job, doc, mem, entity])
    await async_db.commit()

    # 3. Fetch project overview metrics
    overview = await proj_repo.get_project_overview(project.id)
    assert overview["project"]["name"] == "CRISPR Therapeutics"
    assert overview["metrics"]["total_jobs"] == 1
    assert overview["metrics"]["total_documents"] == 1
    assert overview["metrics"]["total_memories"] == 1
    assert overview["metrics"]["total_graph_entities"] == 1


@pytest.mark.asyncio
async def test_ensure_default_workspace_and_project(async_db: AsyncSession, sample_user: DBUser):
    ws_repo = WorkspaceRepository(async_db)
    proj_repo = ProjectRepository(async_db)

    # 1. Automatically provision default workspace
    default_ws = await ws_repo.ensure_default_workspace(sample_user.id, sample_user.username)
    assert default_ws.name == "Alice's Workspace"
    assert default_ws.is_personal is True

    # 2. Calling again returns the existing workspace
    same_ws = await ws_repo.ensure_default_workspace(sample_user.id, sample_user.username)
    assert same_ws.id == default_ws.id

    # 3. Automatically provision default project
    default_proj = await proj_repo.ensure_default_project(default_ws.id, sample_user.id)
    assert default_proj.name == "General Research"
    assert default_proj.slug == "general-research"
