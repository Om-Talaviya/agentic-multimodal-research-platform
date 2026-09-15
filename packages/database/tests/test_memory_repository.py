"""Tests for persistent MemoryRepository and DBResearchMemory model."""

import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.models.user import User as DBUser
from database.models.memory import DBResearchMemory
from database.repositories.memory_repository import MemoryRepository
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
        username="researcher_alice",
        email="alice@example.com",
        password_hash=hash_password("StrongPass123!"),
        role=UserRole.RESEARCHER.value,
        is_active=True,
    )
    created = await user_repo.create(user)
    await async_db.commit()
    return created


@pytest.mark.asyncio
async def test_memory_lifecycle_and_crud(async_db: AsyncSession, sample_user: DBUser):
    repo = MemoryRepository(async_db)

    memory = DBResearchMemory(
        user_id=sample_user.id,
        memory_type="finding",
        title="Federated Learning Convergence",
        content="Non-IID client data increases communication rounds by 40% under standard FedAvg.",
        confidence_score=0.92,
        tags=["federated-learning", "convergence", "non-iid"],
        provenance_json={"domain": "distributed-ai", "sources_analyzed": 5},
        is_pinned=True,
    )

    created = await repo.create(memory)
    await async_db.commit()

    assert created.id is not None
    assert created.user_id == sample_user.id
    assert created.memory_type == "finding"
    assert created.is_pinned is True
    assert "non-iid" in created.tags

    # Fetch by ID
    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.title == "Federated Learning Convergence"

    # List for User
    user_memories = await repo.list_for_user(sample_user.id)
    assert len(user_memories) == 1
    assert user_memories[0].id == created.id

    # Update Memory
    updated = await repo.update(
        memory_id=created.id,
        user_id=sample_user.id,
        content="Non-IID client data increases communication rounds by 42% under standard FedAvg.",
        confidence_score=0.95,
        is_pinned=False,
    )
    await async_db.commit()

    assert updated is not None
    assert updated.content.endswith("42% under standard FedAvg.")
    assert updated.confidence_score == 0.95
    assert updated.is_pinned is False

    # Increment Access
    await repo.increment_access(created.id)
    await async_db.commit()
    re_fetched = await repo.get_by_id(created.id)
    assert re_fetched.access_count == 1
    assert re_fetched.last_accessed_at is not None

    # Delete
    deleted = await repo.delete(created.id, sample_user.id)
    await async_db.commit()
    assert deleted is True
    assert await repo.get_by_id(created.id) is None


@pytest.mark.asyncio
async def test_memory_batch_create_and_filters(async_db: AsyncSession, sample_user: DBUser):
    repo = MemoryRepository(async_db)

    memories = [
        DBResearchMemory(
            user_id=sample_user.id,
            memory_type="concept",
            title="Reciprocal Rank Fusion",
            content="RRF combines rankings from disparate retrieval algorithms using $1 / (k + rank)$.",
            confidence_score=0.98,
            tags=["rag", "rrf", "hybrid-search"],
            is_pinned=True,
        ),
        DBResearchMemory(
            user_id=sample_user.id,
            memory_type="hypothesis",
            title="Sub-quadratic Attention Hypothesis",
            content="State Space Models scale to 1M context with O(N) memory complexity.",
            confidence_score=0.85,
            tags=["transformers", "ssm", "mamba"],
            is_pinned=False,
        ),
        DBResearchMemory(
            user_id=sample_user.id,
            memory_type="fact",
            title="SQLite Locking Model",
            content="SQLite uses serialized file locks during write transactions.",
            confidence_score=0.99,
            tags=["database", "sqlite", "concurrency"],
            is_pinned=False,
        ),
    ]

    await repo.batch_create(memories)
    await async_db.commit()

    # Filter by memory type
    concepts = await repo.list_for_user(sample_user.id, memory_type="concept")
    assert len(concepts) == 1
    assert concepts[0].title == "Reciprocal Rank Fusion"

    # Filter by pinned
    pinned = await repo.list_for_user(sample_user.id, is_pinned=True)
    assert len(pinned) == 1
    assert pinned[0].title == "Reciprocal Rank Fusion"

    # Filter by tag
    db_memories = await repo.list_for_user(sample_user.id, tag="sqlite")
    assert len(db_memories) == 1
    assert db_memories[0].title == "SQLite Locking Model"

    # Search by text
    search_results = await repo.search_by_text(sample_user.id, "sub-quadratic")
    assert len(search_results) == 1
    assert search_results[0].title == "Sub-quadratic Attention Hypothesis"

    # Count
    count = await repo.count_for_user(sample_user.id)
    assert count == 3
