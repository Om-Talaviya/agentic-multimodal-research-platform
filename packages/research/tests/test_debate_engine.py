"""Unit tests for DebateEngine and Elo calculations."""

import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from agents.base import AgentContext
from database.connection import Base
from database.models.user import User
from database.repositories.debate_repo import DebateRepository
from research.debate.engine import DebateEngine, compute_elo_shift


@pytest.mark.asyncio
async def test_compute_elo_shift():
    """Test standard Elo calculations for debate scoring."""
    # Equal ratings, A wins
    delta_a, new_a, new_b = compute_elo_shift(1500.0, 1500.0, score_a=0.9, score_b=0.7, k_factor=32.0)
    assert delta_a == 16.0
    assert new_a == 1516.0
    assert new_b == 1484.0

    # Draw
    delta_a_draw, new_a_draw, new_b_draw = compute_elo_shift(1500.0, 1500.0, score_a=0.8, score_b=0.8, k_factor=32.0)
    assert delta_a_draw == 0.0
    assert new_a_draw == 1500.0
    assert new_b_draw == 1500.0


@pytest.mark.asyncio
async def test_debate_engine_execution():
    """Test DebateEngine running rounds and generating consensus."""
    engine_db = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine_db.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(
        engine_db, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_factory() as session:
        user = User(
            id=uuid.uuid4(),
            username="researcher_arena",
            email="researcher@arena.ai",
            password_hash="pw",
            role="researcher",
        )
        session.add(user)
        await session.commit()

        repo = DebateRepository(session)
        debate = await repo.create_debate(
            user_id=user.id,
            topic="Quantum Advantage in Prime Factorization",
            initial_thesis="Shor's algorithm with logical qubit error correction achieves polynomial-time factorization.",
            max_rounds=2,
        )

        context = AgentContext(user_id=user.id)
        engine = DebateEngine(debate_repo=repo)

        # Round 1
        res1 = await engine.execute_round(debate.id, context)
        assert res1["round_number"] == 1
        assert res1["is_concluded"] is False

        # Round 2 (Concluding)
        res2 = await engine.execute_round(debate.id, context)
        assert res2["round_number"] == 2
        assert res2["is_concluded"] is True
        assert res2["consensus"] is not None
        assert "consensus_statement" in res2["consensus"]

        updated_debate = await repo.get_debate(debate.id)
        assert updated_debate.status == "concluded"
        assert updated_debate.current_round == 2

    await engine_db.dispose()
