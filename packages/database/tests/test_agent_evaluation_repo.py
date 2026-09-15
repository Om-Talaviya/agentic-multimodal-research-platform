"""Tests for AgentEvaluationRepository."""
from datetime import UTC, datetime
from uuid import uuid4
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.connection import Base
from database.models.agent_evaluation import DBAgentEvaluation, DBAgentStepMetric
from database.models.user import User as DBUser
from database.repositories.agent_evaluation_repo import AgentEvaluationRepository
from database.repositories.user_repo import UserRepository
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
async def test_user(async_db: AsyncSession) -> DBUser:
    user_repo = UserRepository(async_db)
    user = DBUser(
        username="agent_eval_tester",
        email="agent_eval@example.com",
        password_hash=hash_password("Pass12345!"),
        role=UserRole.ADMIN.value,
        is_active=True,
    )
    created = await user_repo.create(user)
    await async_db.commit()
    return created


@pytest.mark.asyncio
async def test_agent_evaluation_repository_crud(async_db: AsyncSession, test_user: DBUser):
    repo = AgentEvaluationRepository(async_db)

    step_telemetry = [
        {
            "step_index": 0,
            "agent_type": "ResearchPipeline",
            "action_type": "tool_execution",
            "tool_name": "web_search",
            "tool_args": {"query": "deep learning"},
            "tool_output_length": 250,
            "success": True,
            "error_message": None,
            "latency_ms": 150,
            "tokens_consumed": 45,
        },
        {
            "step_index": 1,
            "agent_type": "ResearchPipeline",
            "action_type": "synthesis",
            "tool_name": "synthesize",
            "tool_args": {},
            "tool_output_length": 500,
            "success": True,
            "error_message": None,
            "latency_ms": 320,
            "tokens_consumed": 120,
        },
    ]

    # 1. Create agent evaluation
    eval_rec = await repo.create_evaluation(
        agent_name="ResearchPipeline",
        total_steps=2,
        successful_steps=2,
        failed_steps=0,
        plan_precision=1.0,
        tool_accuracy=1.0,
        evidence_coverage=0.95,
        hallucination_rate=0.05,
        synthesis_fidelity=0.95,
        overall_score=0.975,
        execution_time_ms=470,
        total_tokens=165,
        estimated_cost_usd=0.00003,
        findings_audit={"claims_evaluated": 2, "evidence_sources": 1},
        job_id=None,
        evaluated_by=test_user.id,
        step_telemetry=step_telemetry,
    )

    assert eval_rec.id is not None
    assert eval_rec.agent_name == "ResearchPipeline"
    assert eval_rec.overall_score == 0.975

    # 2. Get evaluation by ID with step metrics
    retrieved = await repo.get_evaluation_by_id(eval_rec.id)
    assert retrieved is not None
    assert retrieved.agent_name == "ResearchPipeline"
    assert len(retrieved.steps) == 2
    assert retrieved.steps[0].tool_name == "web_search"

    # 3. List evaluations
    listed = await repo.list_evaluations(agent_name="ResearchPipeline")
    assert len(listed) >= 1
    assert listed[0].id == eval_rec.id

    # 4. Get metrics summary
    summary = await repo.get_agent_metrics_summary()
    assert summary["total_evaluations"] == 1
    assert summary["avg_score"] == 0.975

    # 5. Delete evaluation
    deleted = await repo.delete_evaluation(eval_rec.id)
    assert deleted is True
    assert await repo.get_evaluation_by_id(eval_rec.id) is None
