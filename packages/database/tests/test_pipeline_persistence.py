"""Integration tests for ResearchPipeline database persistence with real models and sessions."""

from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from agents.base import AgentResult
from database.connection import Base
from database.models import ResearchJob as DBResearchJob, Source as DBSource, Evidence as DBEvidence
from database.repositories import (
    ResearchJobRepository,
    TaskRepository,
    SourceRepository,
    EvidenceRepository,
)
from research.models import (
    Evidence as PydanticEvidence,
    ResearchJob as PydanticResearchJob,
    ResearchPlan,
    ResearchRequest,
    ResearchStep,
    Source as PydanticSource,
)
from research.pipeline import ResearchPipeline


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


@pytest.mark.asyncio
async def test_pipeline_create_job_and_execute_plan_persists_sources_and_evidence(test_db):
    """Test full execute_plan persists DBResearchTask, DBSource, and DBEvidence properly."""
    orchestrator = MagicMock()
    agent_registry = MagicMock()
    tool_registry = MagicMock()
    model_router = MagicMock()

    orchestrator.create_context = MagicMock(return_value=MagicMock())

    pipeline = ResearchPipeline(
        orchestrator=orchestrator,
        agent_registry=agent_registry,
        tool_registry=tool_registry,
        model_router=model_router,
    )

    # 1. Create Job
    req = ResearchRequest(
        question="What is multimodal agentic AI?",
        constraints=["focus on recent advancements"],
    )
    job = await pipeline.create_job(req)
    job_uuid = UUID(job.id)

    # Verify job persisted in DB
    async with test_db() as session:
        job_repo = ResearchJobRepository(session)
        db_job = await job_repo.get(job_uuid)
        assert db_job is not None
        assert db_job.question == req.question

    # 2. Simulate agent returning Pydantic Source and Evidence
    src_id = str(uuid4())
    pydantic_sources = [
        PydanticSource(
            id=src_id,
            type="web",
            url="https://arxiv.org/abs/2401.00000",
            title="Multimodal Agents Paper",
            metadata={"domain": "arxiv.org", "snippet": "Multimodal agents combine vision and text"},
        )
    ]
    pydantic_evidence = [
        PydanticEvidence(
            id=str(uuid4()),
            source_id=src_id,
            claim="Multimodal agents achieve higher accuracy on vision-language tasks",
            supporting_text="Experiments demonstrate 92% benchmark accuracy.",
            confidence=0.92,
            verification_status="verified",
            verification_notes="Empirically verified in benchmark",
        )
    ]

    async def mock_run_agent(agent_name, task, context):
        return AgentResult(
            success=True,
            output={
                "sources": pydantic_sources,
                "evidence": pydantic_evidence,
            },
        )

    orchestrator.run_agent = AsyncMock(side_effect=mock_run_agent)

    # 3. Execute Plan
    plan = ResearchPlan(
        objective="Analyze multimodal agent research",
        steps=[
            ResearchStep(id="step_1", name="Web Search", description="Search Arxiv", agent="web_research", depends_on=[]),
        ],
    )

    await pipeline.execute_plan(job, plan)

    # 4. Verify sources and evidence were converted and persisted in database
    async with test_db() as session:
        source_repo = SourceRepository(session)
        evidence_repo = EvidenceRepository(session)
        task_repo = TaskRepository(session)

        # Verify tasks
        tasks = await task_repo.get_by_job(job_uuid)
        assert len(tasks) == 1
        assert tasks[0].status == "completed"

        # Verify sources
        db_sources = await source_repo.get_by_job(job_uuid)
        assert len(db_sources) == 1
        assert str(db_sources[0].id) == src_id
        assert db_sources[0].url == "https://arxiv.org/abs/2401.00000"
        assert db_sources[0].job_id == job_uuid
        assert db_sources[0].source_metadata.get("domain") == "arxiv.org"

        # Verify evidence
        db_evidence = await evidence_repo.get_by_job(job_uuid)
        assert len(db_evidence) == 1
        assert db_evidence[0].job_id == job_uuid
        assert str(db_evidence[0].source_id) == src_id
        assert db_evidence[0].confidence == 0.92
        assert db_evidence[0].verification_status == "verified"


@pytest.mark.asyncio
async def test_pipeline_run_report_generation_persists_report(test_db):
    """Test run_report_generation runs ReportAgent and persists Report model into database."""
    from database.repositories import ReportRepository
    from database.models import Report as DBReport

    orchestrator = MagicMock()
    agent_registry = MagicMock()
    tool_registry = MagicMock()
    model_router = MagicMock()

    orchestrator.create_context = MagicMock(return_value=MagicMock())

    pipeline = ResearchPipeline(
        orchestrator=orchestrator,
        agent_registry=agent_registry,
        tool_registry=tool_registry,
        model_router=model_router,
    )

    # 1. Create Job, Sources, Evidence
    req = ResearchRequest(question="What are modern reasoning LLMs?")
    job = await pipeline.create_job(req)
    job_uuid = UUID(job.id)

    src_id = uuid4()
    ev_id = uuid4()

    async with test_db() as session:
        source_repo = SourceRepository(session)
        evidence_repo = EvidenceRepository(session)

        await source_repo.create(DBSource(
            id=src_id,
            job_id=job_uuid,
            type="web",
            url="https://example.com/reasoning",
            title="Reasoning LLMs Overview",
        ))
        await evidence_repo.create(DBEvidence(
            id=ev_id,
            job_id=job_uuid,
            source_id=src_id,
            claim="Chain-of-thought fine-tuning enhances multi-step reasoning capabilities.",
            supporting_text="Benchmark results show 35% improvement on math reasoning.",
            confidence=0.95,
            verification_status="verified",
        ))

    # 2. Mock ReportAgent execution result
    report_output = {
        "title": "Research Report: Reasoning LLMs",
        "executive_summary": "Reasoning LLMs demonstrate significant gains via search and CoT.",
        "methodology": "Literature synthesis and verified evidence extraction.",
        "findings": [
            {
                "topic": "Chain of Thought",
                "summary": "CoT improves complex reasoning tasks [ev_id].",
                "evidence_ids": [str(ev_id)],
                "confidence": 0.95,
                "uncertainty": None,
                "assumptions": [],
            }
        ],
        "evidence_ids": [str(ev_id)],
        "source_ids": [str(src_id)],
        "conclusions": ["Reasoning models excel at multi-step problems."],
        "limitations": ["Inference compute costs are higher."],
    }

    orchestrator.run_agent = AsyncMock(return_value=AgentResult(
        success=True,
        output=report_output,
    ))

    # 3. Run report generation
    await pipeline.run_report_generation(job)

    # 4. Verify report was persisted in DB
    async with test_db() as session:
        report_repo = ReportRepository(session)
        db_report = await report_repo.get_by_job(job_uuid)

        assert db_report is not None
        assert db_report.job_id == job_uuid
        assert db_report.title == "Research Report: Reasoning LLMs"
        assert db_report.executive_summary == "Reasoning LLMs demonstrate significant gains via search and CoT."
        assert len(db_report.findings) == 1
        assert str(ev_id) in db_report.evidence_ids
        assert str(src_id) in db_report.source_ids
        assert db_report.conclusions == ["Reasoning models excel at multi-step problems."]
        assert db_report.limitations == ["Inference compute costs are higher."]


@pytest.mark.asyncio
async def test_pipeline_run_report_generation_handles_empty_evidence(test_db):
    """Test run_report_generation handles zero evidence without crashing."""
    from database.repositories import ReportRepository

    orchestrator = MagicMock()
    agent_registry = MagicMock()
    tool_registry = MagicMock()
    model_router = MagicMock()

    orchestrator.create_context = MagicMock(return_value=MagicMock())

    pipeline = ResearchPipeline(
        orchestrator=orchestrator,
        agent_registry=agent_registry,
        tool_registry=tool_registry,
        model_router=model_router,
    )

    req = ResearchRequest(question="Question with no evidence")
    job = await pipeline.create_job(req)
    job_uuid = UUID(job.id)

    orchestrator.run_agent = AsyncMock(return_value=AgentResult(
        success=True,
        output={
            "title": "Research Report: Question with no evidence",
            "executive_summary": "No evidence was gathered for this research question.",
            "methodology": "No research was conducted due to lack of available evidence.",
            "findings": [],
            "evidence_ids": [],
            "source_ids": [],
            "conclusions": [],
            "limitations": ["No evidence available to support any findings."],
        },
    ))

    await pipeline.run_report_generation(job)

    async with test_db() as session:
        report_repo = ReportRepository(session)
        db_report = await report_repo.get_by_job(job_uuid)

        assert db_report is not None
        assert db_report.job_id == job_uuid
        assert db_report.findings == []
        assert db_report.evidence_ids == []
