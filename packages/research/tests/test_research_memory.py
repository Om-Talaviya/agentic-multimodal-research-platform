"""Unit tests for Research Memory manager and models (Phase 16)."""

import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from database.connection import Base
from database.models.user import User as DBUser
from database.repositories.user_repo import UserRepository
from database.repositories.memory_repository import MemoryRepository
from shared.auth import hash_password, UserRole
from research.memory.models import MemoryItem, MemoryType, MemoryRecallResult
from research.memory.manager import ResearchMemoryManager


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
        username="researcher_bob",
        email="bob@example.com",
        password_hash=hash_password("Pass123!"),
        role=UserRole.RESEARCHER.value,
        is_active=True,
    )
    created = await user_repo.create(user)
    await async_db.commit()
    return created


@pytest.mark.asyncio
async def test_memory_models_instantiation():
    item = MemoryItem(
        id=str(uuid4()),
        user_id=str(uuid4()),
        job_id=str(uuid4()),
        memory_type=MemoryType.INSIGHT,
        title="Test Memory Title",
        content="Test finding content regarding neural architecture search",
        tags=["nas", "automl"],
        confidence=0.92,
        source_type="report",
    )
    assert item.title == "Test Memory Title"
    assert item.memory_type == MemoryType.INSIGHT
    assert item.confidence == 0.92
    assert "nas" in item.tags

    dumped = item.model_dump(mode="json")
    assert dumped["memory_type"] == "insight"


@pytest.mark.asyncio
async def test_format_memories_for_prompt():
    mgr = ResearchMemoryManager()
    memories = [
        MemoryItem(
            id=str(uuid4()),
            memory_type=MemoryType.FINDING,
            title="Transformer Scaling Laws",
            content="Loss scales as a power-law with parameters and tokens.",
            tags=["llm", "scaling"],
            confidence=0.95,
        ),
        MemoryItem(
            id=str(uuid4()),
            memory_type=MemoryType.METHODOLOGY,
            title="Direct Preference Optimization",
            content="Implicitly optimizes reward using reference policy log-odds.",
            tags=["rlhf", "dpo"],
            confidence=0.88,
        ),
    ]

    formatted = mgr.format_memories_for_prompt(memories)
    assert "Prior Research Finding" in formatted
    assert "Prior Research Methodology" in formatted
    assert "Transformer Scaling Laws" in formatted
    assert "Direct Preference Optimization" in formatted


@pytest.mark.asyncio
async def test_store_and_recall_memories_integration(async_db: AsyncSession, sample_user: DBUser):
    repo = MemoryRepository(async_db)
    mgr = ResearchMemoryManager(session_or_repo=repo)

    # Store a concept memory
    mem1 = await mgr.store_memory(
        title="Quantum Approximate Optimization Algorithm",
        content="QAOA uses alternating cost and mixer Hamiltonians with variational angle parameters.",
        memory_type=MemoryType.CONCEPT,
        user_id=sample_user.id,
        tags=["quantum", "qaoa", "optimization"],
        confidence=0.95,
    )
    await async_db.commit()
    assert mem1.title == "Quantum Approximate Optimization Algorithm"
    assert mem1.tags == ["quantum", "qaoa", "optimization"]

    # Store a finding memory
    mem2 = await mgr.store_memory(
        title="QAOA Depth p=3 Benchmark",
        content="Approximation ratio reaches 0.82 on 3-regular Max-Cut graphs at p=3.",
        memory_type=MemoryType.FINDING,
        user_id=sample_user.id,
        tags=["quantum", "benchmarks"],
        confidence=0.9,
    )
    await async_db.commit()
    assert mem2.title == "QAOA Depth p=3 Benchmark"

    # Recall by semantic/text query
    recall_res = await mgr.recall_memories(
        user_id=sample_user.id,
        query="Hamiltonian angles optimization",
        top_k=5,
    )
    assert isinstance(recall_res, MemoryRecallResult)
    assert len(recall_res.memories) >= 1
    titles = [m.title for m in recall_res.memories]
    assert "Quantum Approximate Optimization Algorithm" in titles


@pytest.mark.asyncio
async def test_store_memories_from_report(async_db: AsyncSession, sample_user: DBUser):
    repo = MemoryRepository(async_db)
    mgr = ResearchMemoryManager(session_or_repo=repo)

    report_data = {
        "title": "Quantum Supremacy & QAOA State of the Art",
        "executive_summary": "Comprehensive overview of quantum heuristics and empirical speedups.",
        "methodology": "Simulated statevector state evolution with PennyLane on noiseless simulators.",
        "findings": [
            "QAOA achieves faster convergence with warm-started initialization.",
            "Barren plateaus remain a key challenge for random initial angles.",
        ],
        "conclusions": [
            "Hybrid classical-quantum algorithms show near-term promise on NISQ hardware."
        ],
    }

    stored_items = await mgr.store_memories_from_report(
        user_id=sample_user.id,
        report_data=report_data,
        confidence_score=0.88,
    )
    await async_db.commit()

    assert len(stored_items) >= 3
    types = [m.memory_type.value for m in stored_items]
    assert "summary" in types
    assert "methodology" in types
    assert "finding" in types
