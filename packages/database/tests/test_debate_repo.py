"""Unit tests for DebateRepository and database models."""

import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.models.user import User
from database.models.workspace import DBWorkspace
from database.repositories.debate_repo import DebateRepository


@pytest.fixture
async def db_session():
    """Create in-memory SQLite database session for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_debate_repo_lifecycle(db_session: AsyncSession):
    """Test full CRUD and round/consensus lifecycle in DebateRepository."""
    user = User(
        id=uuid.uuid4(),
        username="debater_test",
        email="debater@test.com",
        password_hash="hashed_pw",
        role="researcher",
    )
    db_session.add(user)
    await db_session.commit()

    repo = DebateRepository(db_session)

    # 1. Create Debate
    debate = await repo.create_debate(
        user_id=user.id,
        topic="Solid State Batteries vs Lithium-Ion",
        initial_thesis="Solid state electrolytes provide superior energy density and thermal safety.",
        counter_thesis="Manufacturing scalability and dendrite penetration at high C-rates remain unsolved.",
        max_rounds=2,
    )
    assert debate.id is not None
    assert debate.status == "active"
    assert debate.proposer_elo == 1500.0
    assert debate.opposer_elo == 1500.0

    # 2. Add Round 1
    round_1 = await repo.add_debate_round(
        debate_id=debate.id,
        round_number=1,
        proposer_argument="Silicon-anode solid-state cells demonstrated 450 Wh/kg in 2026 trials.",
        opposer_argument="Dendrite formation at >3C charging causes catastrophic short circuits.",
        proposer_citations=[{"title": "Battery Lab 2026", "snippet": "450 Wh/kg confirmed"}],
        opposer_citations=[{"title": "Dendrite Study", "snippet": "Dendrites form at 3C"}],
        proposer_score=0.85,
        opposer_score=0.82,
        arbiter_critique="Proposer proved energy density; Opposer raised critical rate limits.",
        round_winner="proposer",
        elo_delta=16.0,
    )
    assert round_1.id is not None
    assert round_1.round_winner == "proposer"

    # 3. Update Debate Status
    await repo.update_debate_status(
        debate_id=debate.id,
        status="active",
        current_round=1,
        proposer_elo=1516.0,
        opposer_elo=1484.0,
    )

    # 4. Record Consensus
    consensus = await repo.record_consensus(
        debate_id=debate.id,
        consensus_statement="Solid state batteries provide superior density but currently require constrained charging rates.",
        accepted_claims=[{"claim": "450 Wh/kg achieved", "confidence": 0.95}],
        refuted_claims=[{"claim": "Unconstrained fast-charging", "reason": "Dendrite risk"}],
        concessions=[{"side": "proposer", "point": "Fast-charge limitation"}],
        remaining_uncertainties=["Solid electrolyte degradation over 2,000 cycles"],
        overall_confidence=0.91,
        winner_overall="balanced_consensus",
        final_proposer_elo=1516.0,
        final_opposer_elo=1484.0,
    )
    assert consensus.id is not None
    assert consensus.overall_confidence == 0.91

    # 5. Verify Metrics
    metrics = await repo.get_debate_metrics(user_id=user.id)
    assert metrics["total_debates"] == 1
    assert metrics["concluded_debates"] == 1
    assert metrics["mean_confidence"] == 0.91

    # 6. Delete Debate
    deleted = await repo.delete_debate(debate.id)
    assert deleted is True
    assert (await repo.get_debate(debate.id)) is None
