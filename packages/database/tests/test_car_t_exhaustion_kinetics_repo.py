"""Tests for Phase 183: CAR-T Cell Exhaustion Repository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.car_t_exhaustion_kinetics_repo import CARTExhaustionKineticsRepository


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
async def test_car_t_exhaustion_kinetics_repo_crud(async_db: AsyncSession):
    repo = CARTExhaustionKineticsRepository(async_db)

    study = await repo.create_study(
        name="anti-CD19-41BBz Test Study",
        car_construct_name="anti-CD19-41BBz",
        costimulatory_domain="4-1BB",
        t_stem_cell_memory_pct=38.5,
        tox_nr4a_epigenetic_exhaustion_score=0.24,
        predicted_persistence_half_life_days=185.0,
    )
    await async_db.commit()

    assert study.id is not None
    assert study.car_construct_name == "anti-CD19-41BBz"

    state = await repo.add_differentiation_state(
        study_id=study.id,
        state_name="Tscm (Stem Memory)",
        population_percentage=38.5,
        tcf7_expression_level=0.94,
        proliferative_capacity_score=0.96,
        cytolytic_granzyme_b_score=0.35,
    )
    await async_db.commit()

    assert state.id is not None
    assert state.state_name == "Tscm (Stem Memory)"

    marker = await repo.add_checkpoint_marker(
        study_id=study.id,
        marker_symbol="TOX",
        surface_density_molecules=1200.0,
        epigenetic_chromatin_accessibility_score=0.24,
        reversibility_potential_pct=72.0,
    )
    await async_db.commit()

    assert marker.id is not None

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "anti-CD19-41BBz Test Study"

    studies = await repo.list_studies()
    assert len(studies) >= 1