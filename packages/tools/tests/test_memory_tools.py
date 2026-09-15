"""Unit tests for RecallMemoryTool and StoreMemoryTool (Phase 16)."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from database.connection import Base
from database.models.user import User as DBUser
from database.repositories.user_repo import UserRepository
from database.repositories.memory_repository import MemoryRepository
from shared.auth import hash_password, UserRole
from tools.definitions.memory import RecallMemoryTool, StoreMemoryTool
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
        username="tool_tester",
        email="tester@example.com",
        password_hash=hash_password("Pass123!"),
        role=UserRole.RESEARCHER.value,
        is_active=True,
    )
    created = await user_repo.create(user)
    await async_db.commit()
    return created


@pytest.mark.asyncio
async def test_store_and_recall_memory_tools(async_db: AsyncSession, sample_user: DBUser):
    repo = MemoryRepository(async_db)
    mem_mgr = ResearchMemoryManager(session_or_repo=repo)
    store_tool = StoreMemoryTool(memory_manager=mem_mgr)
    recall_tool = RecallMemoryTool(memory_manager=mem_mgr)

    # 1. Test StoreMemoryTool
    store_result = await store_tool.execute(
        title="Zero-Shot Cross-Lingual Transfer in LLMs",
        content="Cross-lingual representations align semantics across 100+ languages without parallel text.",
        memory_type="insight",
        tags=["nlp", "cross-lingual", "multilingual"],
        confidence=0.94,
        user_id=str(sample_user.id),
    )
    await async_db.commit()

    assert store_result.get("success") is True
    assert "memory_id" in store_result
    assert store_result.get("title") == "Zero-Shot Cross-Lingual Transfer in LLMs"

    # 2. Test RecallMemoryTool
    recall_result = await recall_tool.execute(
        query="cross-lingual multilingual representations",
        top_k=5,
        user_id=str(sample_user.id),
    )

    assert isinstance(recall_result, list)
    assert len(recall_result) >= 1
    recalled_item = recall_result[0]
    assert recalled_item["title"] == "Zero-Shot Cross-Lingual Transfer in LLMs"
    assert "nlp" in recalled_item["tags"]


@pytest.mark.asyncio
async def test_recall_memory_tool_filters(async_db: AsyncSession, sample_user: DBUser):
    repo = MemoryRepository(async_db)
    mem_mgr = ResearchMemoryManager(session_or_repo=repo)
    store_tool = StoreMemoryTool(memory_manager=mem_mgr)
    recall_tool = RecallMemoryTool(memory_manager=mem_mgr)

    await store_tool.execute(
        title="BFT Consensus Throughput",
        content="Byzantine Fault Tolerant consensus reaches 10,000 TPS under optimistic conditions.",
        memory_type="finding",
        tags=["distributed", "consensus"],
        user_id=str(sample_user.id),
    )
    await async_db.commit()

    # Search with mismatched type filter
    filtered_out = await recall_tool.execute(
        query="BFT consensus",
        memory_type="hypothesis",
        user_id=str(sample_user.id),
    )
    assert len(filtered_out) == 0

    # Search with matching type filter
    filtered_in = await recall_tool.execute(
        query="BFT consensus",
        memory_type="finding",
        user_id=str(sample_user.id),
    )
    assert len(filtered_in) >= 1
