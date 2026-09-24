"""Tests for SingleMoleculeFRETRepository (Phase 160)."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.single_molecule_fret_repo import SingleMoleculeFRETRepository


@pytest_asyncio.fixture
async def async_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_single_molecule_fret_repo_lifecycle(async_db: AsyncSession):
    repo = SingleMoleculeFRETRepository(async_db)

    study = await repo.create_study(
        biomolecule_name="Hsp90 Dimer",
        donor_fluorophore="Cy3",
        acceptor_fluorophore="Cy5",
        forster_distance_r0_nm=5.4,
        molecules_analyzed_count=1000,
        mean_fret_efficiency=0.45,
        transition_rate_k_open_s=2.0,
        transition_rate_k_close_s=5.0,
    )
    assert study.id is not None

    await repo.add_state_transition(
        study_id=study.id,
        state_label="Open State",
        fret_efficiency_peak=0.2,
        mean_dwell_time_ms=400.0,
        state_occupancy_percentage=60.0,
        apparent_distance_angstrom=65.0,
    )

    await repo.add_trajectory(
        study_id=study.id,
        molecule_index=1,
        donor_lifetime_seconds=15.0,
        acceptor_lifetime_seconds=10.0,
        total_transitions_observed=20,
        single_step_photobleaching=True,
    )

    loaded = await repo.get_study_with_details(study.id)
    assert loaded is not None
    assert len(loaded.state_transitions) == 1
    assert len(loaded.trajectories) == 1
