"""Unit tests for ReproducibilityRepository and database models."""

import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.models.user import User
from database.repositories.reproducibility_repo import ReproducibilityRepository


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
async def test_reproducibility_repo_lifecycle(db_session: AsyncSession):
    """Test creating protocol, recording execution run, and storing claim verification traces."""
    user = User(
        id=uuid.uuid4(),
        username="experimenter_test",
        email="exp@test.com",
        password_hash="hashed_pw",
        role="researcher",
    )
    db_session.add(user)
    await db_session.commit()

    repo = ReproducibilityRepository(db_session)

    # 1. Create Protocol
    protocol = await repo.create_protocol(
        user_id=user.id,
        name="Monte Carlo Option Pricing Verification",
        executable_code="""import math, random
def price(s0=100, k=100, r=0.05, t=1.0, sigma=0.2, n=10000):
    drift = (r - 0.5 * sigma**2) * t
    vol = sigma * math.sqrt(t)
    payoffs = [max(0, s0 * math.exp(drift + vol * random.gauss(0, 1)) - k) for _ in range(n)]
    return math.exp(-r * t) * (sum(payoffs) / n)
metrics = {'call_price': round(price(), 2)}
""",
        parameters={"s0": 100, "k": 100, "n": 10000},
        claimed_metrics={"call_price": 10.45},
    )
    assert protocol.id is not None
    assert protocol.name == "Monte Carlo Option Pricing Verification"
    assert protocol.verification_status == "unverified"

    # 2. Record Reproducibility Run
    run = await repo.record_reproducibility_run(
        protocol_id=protocol.id,
        executed_by=user.id,
        status="succeeded",
        execution_time_ms=12.5,
        memory_peak_mb=18.4,
        reproduced_metrics={"call_price": 10.42},
        reproducibility_score=0.98,
        runtime_logs="Simulation completed with 10,000 paths.",
    )
    assert run.id is not None
    assert run.status == "succeeded"

    # 3. Record Claim Verification Trace
    trace = await repo.record_verification_trace(
        protocol_id=protocol.id,
        run_id=run.id,
        claim_statement="Claimed call_price = 10.45",
        metric_name="call_price",
        claimed_value=10.45,
        reproduced_value=10.42,
        delta_relative_error=0.0028,
        tolerance_threshold=0.05,
        verdict="reproduced",
        analysis_notes="Delta error of 0.28% within 5.0% threshold.",
    )
    assert trace.id is not None
    assert trace.verdict == "reproduced"

    # 4. Check Eager Retrieval
    fetched_protocol = await repo.get_protocol(protocol.id)
    assert len(fetched_protocol.runs) == 1
    assert len(fetched_protocol.verification_traces) == 1

    # 5. Check Metrics
    metrics = await repo.get_reproducibility_metrics()
    assert metrics["total_protocols"] == 1
    assert metrics["total_runs"] == 1
    assert metrics["total_verified_claims"] == 1
    assert metrics["reproduced_claims"] == 1
    assert metrics["claim_reproducibility_rate"] == 100.0
