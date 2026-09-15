"""Tests for ModelEvaluationRepository."""
from datetime import UTC, datetime
from uuid import uuid4
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.connection import Base
from database.models.evaluation import DBModelBenchmarkResult, DBModelEvaluation
from database.models.user import User as DBUser
from database.repositories.evaluation_repo import ModelEvaluationRepository
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
        username="eval_tester",
        email="eval@example.com",
        password_hash=hash_password("Pass12345!"),
        role=UserRole.ADMIN.value,
        is_active=True,
    )
    created = await user_repo.create(user)
    await async_db.commit()
    return created


@pytest.mark.asyncio
async def test_evaluation_repository_crud(async_db: AsyncSession, test_user: DBUser):
    repo = ModelEvaluationRepository(async_db)

    sample_results = [
        {
            "sample_id": "sample_1",
            "category": "factual_recall",
            "prompt": "What is quantum entanglement?",
            "response_text": "Quantum entanglement is a physical phenomenon...",
            "passed": True,
            "score": 0.95,
            "metrics": {"factual_accuracy": 0.95},
            "latency_ms": 120.0,
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "cost_usd": 0.00002,
        },
        {
            "sample_id": "sample_2",
            "category": "reasoning_math",
            "prompt": "Compute 12 * 8",
            "response_text": "96",
            "passed": True,
            "score": 1.0,
            "metrics": {"reasoning_depth": 1.0},
            "latency_ms": 80.0,
            "prompt_tokens": 8,
            "completion_tokens": 2,
            "cost_usd": 0.00001,
        },
    ]

    # 1. Create evaluation
    eval_rec = await repo.create_evaluation(
        model_id="gemini-2.0-flash",
        provider_name="gemini",
        benchmark_name="research_core_eval_v1",
        total_samples=2,
        passed_samples=2,
        pass_rate=1.0,
        overall_score=0.975,
        mean_accuracy=0.95,
        mean_reasoning=1.0,
        mean_faithfulness=0.95,
        mean_citation_precision=1.0,
        mean_latency_ms=100.0,
        total_cost_usd=0.00003,
        category_scores={"factual_recall": 0.95, "reasoning_math": 1.0},
        triggered_by=test_user.id,
        sample_results=sample_results,
    )

    assert eval_rec.id is not None
    assert eval_rec.model_id == "gemini-2.0-flash"
    assert eval_rec.overall_score == 0.975

    # 2. Get evaluation by ID with test cases
    retrieved = await repo.get_evaluation_by_id(eval_rec.id)
    assert retrieved is not None
    assert retrieved.model_id == "gemini-2.0-flash"
    assert len(retrieved.results) == 2

    # 3. List evaluations
    listed = await repo.list_evaluations(model_id="gemini-2.0-flash")
    assert len(listed) >= 1

    # 4. Get latest per model
    latest_list = await repo.get_latest_evaluations_per_model()
    assert len(latest_list) == 1
    assert latest_list[0].model_id == "gemini-2.0-flash"

    # 5. Delete evaluation
    deleted = await repo.delete_evaluation(eval_rec.id)
    assert deleted is True
    assert await repo.get_evaluation_by_id(eval_rec.id) is None
