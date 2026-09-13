from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from agents.base import AgentResult
from database.connection import Base
from database.models import ResearchJob as DBResearchJob
from database.repositories import ResearchJobRepository
from research.models import ResearchJob, ResearchPlan, ResearchStep, ResearchTask
from research.pipeline import ResearchPipeline
from shared.types import JobStatus


@pytest.fixture
async def test_db():
    from database import connection as db_conn

    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    test_session_maker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    orig_engine = db_conn.engine
    orig_maker = db_conn.async_session_maker

    db_conn.engine = test_engine
    db_conn.async_session_maker = test_session_maker

    yield test_session_maker

    db_conn.engine = orig_engine
    db_conn.async_session_maker = orig_maker
    await test_engine.dispose()


@pytest.fixture
def mock_dependencies():
    orchestrator = MagicMock()
    agent_registry = MagicMock()
    tool_registry = MagicMock()
    model_router = MagicMock()

    orchestrator.create_context = MagicMock(return_value=MagicMock())
    return orchestrator, agent_registry, tool_registry, model_router


@pytest.mark.asyncio
async def test_dag_linear_dependency_chain(mock_dependencies, test_db):
    """Test step_1 -> step_2 -> step_3 linear execution chain."""
    orchestrator, agent_registry, tool_registry, model_router = mock_dependencies

    executed_tasks = []

    async def mock_run_agent(agent_name, task, context):
        executed_tasks.append(task.objective)
        return AgentResult(success=True, output={"status": "ok"})

    orchestrator.run_agent = AsyncMock(side_effect=mock_run_agent)

    pipeline = ResearchPipeline(
        orchestrator=orchestrator,
        agent_registry=agent_registry,
        tool_registry=tool_registry,
        model_router=model_router,
    )

    job_uuid = uuid4()
    req_uuid = uuid4()

    async with test_db() as session:
        repo = ResearchJobRepository(session)
        await repo.create(DBResearchJob(
            id=job_uuid,
            request_id=req_uuid,
            question="Linear test",
            objective="Linear test",
            status=JobStatus.PENDING.value,
        ))

    plan = ResearchPlan(
        objective="Linear test",
        steps=[
            ResearchStep(id="step_1", name="Step 1", description="First Step", agent="web_research", depends_on=[]),
            ResearchStep(id="step_2", name="Step 2", description="Second Step", agent="document_analysis", depends_on=["step_1"]),
            ResearchStep(id="step_3", name="Step 3", description="Third Step", agent="report", depends_on=["step_2"]),
        ],
    )

    job = ResearchJob(
        id=str(job_uuid),
        request_id=str(req_uuid),
        question="Linear test",
        objective="Linear test",
    )

    await pipeline.execute_plan(job, plan)

    assert executed_tasks == ["First Step", "Second Step", "Third Step"]


@pytest.mark.asyncio
async def test_dag_multiple_dependencies(mock_dependencies, test_db):
    """Test step_3 depending on both step_1 and step_2."""
    orchestrator, agent_registry, tool_registry, model_router = mock_dependencies

    executed_tasks = []

    async def mock_run_agent(agent_name, task, context):
        executed_tasks.append(task.objective)
        return AgentResult(success=True, output={"status": "ok"})

    orchestrator.run_agent = AsyncMock(side_effect=mock_run_agent)

    pipeline = ResearchPipeline(
        orchestrator=orchestrator,
        agent_registry=agent_registry,
        tool_registry=tool_registry,
        model_router=model_router,
    )

    job_uuid = uuid4()
    req_uuid = uuid4()

    async with test_db() as session:
        repo = ResearchJobRepository(session)
        await repo.create(DBResearchJob(
            id=job_uuid,
            request_id=req_uuid,
            question="Multi dep test",
            objective="Multi dep test",
            status=JobStatus.PENDING.value,
        ))

    plan = ResearchPlan(
        objective="Multi dep test",
        steps=[
            ResearchStep(id="step_1", name="Step 1", description="Task A", agent="web_research", depends_on=[]),
            ResearchStep(id="step_2", name="Step 2", description="Task B", agent="document_analysis", depends_on=[]),
            ResearchStep(id="step_3", name="Step 3", description="Task C (Join)", agent="report", depends_on=["step_1", "step_2"]),
        ],
    )

    job = ResearchJob(
        id=str(job_uuid),
        request_id=str(req_uuid),
        question="Multi dep test",
        objective="Multi dep test",
    )

    await pipeline.execute_plan(job, plan)

    # Task A and Task B must run before Task C
    assert "Task C (Join)" == executed_tasks[-1]
    assert set(executed_tasks[:2]) == {"Task A", "Task B"}


@pytest.mark.asyncio
async def test_dag_circular_dependency_detected(mock_dependencies, test_db):
    """Test circular dependency raises ValueError."""
    orchestrator, agent_registry, tool_registry, model_router = mock_dependencies

    pipeline = ResearchPipeline(
        orchestrator=orchestrator,
        agent_registry=agent_registry,
        tool_registry=tool_registry,
        model_router=model_router,
    )

    job_uuid = uuid4()
    req_uuid = uuid4()

    async with test_db() as session:
        repo = ResearchJobRepository(session)
        await repo.create(DBResearchJob(
            id=job_uuid,
            request_id=req_uuid,
            question="Circular test",
            objective="Circular test",
            status=JobStatus.PENDING.value,
        ))

    plan = ResearchPlan(
        objective="Circular test",
        steps=[
            ResearchStep(id="step_1", name="Step 1", description="Task A", agent="web_research", depends_on=["step_2"]),
            ResearchStep(id="step_2", name="Step 2", description="Task B", agent="document_analysis", depends_on=["step_1"]),
        ],
    )

    job = ResearchJob(
        id=str(job_uuid),
        request_id=str(req_uuid),
        question="Circular test",
        objective="Circular test",
    )

    with pytest.raises(ValueError, match="Circular dependency or no ready tasks"):
        await pipeline.execute_plan(job, plan)
