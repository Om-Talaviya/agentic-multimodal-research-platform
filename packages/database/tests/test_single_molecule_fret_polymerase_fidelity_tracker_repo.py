"""Tests for Phase 576: Autonomous Single-Molecule smFRET High-Fidelity DNA Polymerase Mismatch Proofreading & Exonuclease Kinetic Tracker repository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.single_molecule_fret_polymerase_fidelity_tracker_repo import SingleMoleculeFretPolymeraseFidelityTrackerRepository


@pytest_asyncio.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_single_molecule_fret_polymerase_fidelity_tracker_repository(async_session: AsyncSession):
    repo = SingleMoleculeFretPolymeraseFidelityTrackerRepository(async_session)

    study = await repo.create_study(
        name="Autonomous Single-Molecule smFRET High-Fidelity DNA Polymerase Mismatch Proofreading & Exonuclease Kinetic Tracker Benchmark",
        target_specimen="Dual Cy3/Cy5-Labeled Primer-Template DNA Bound to Thermus aquaticus Polymerase I Active/Exo Sites",
        analytical_modality="smfret-polymerase-fidelity-kinetics",
        fret_efficiency_transition_delta=0.42,
        exonuclease_proofreading_dwell_time_ms=85.0,
        mismatch_discrimination_factor=340.0,
        polymerization_catalytic_rate_nt_s=65.0,
        confidence_score=0.997,
        status="completed",
        summary_report="Automated validation benchmark passed successfully.",
    )
    assert study.id is not None
    assert study.name == "Autonomous Single-Molecule smFRET High-Fidelity DNA Polymerase Mismatch Proofreading & Exonuclease Kinetic Tracker Benchmark"
    assert study.fret_efficiency_transition_delta == 0.42
    assert study.confidence_score == 0.997

    profile = await repo.add_item_profile(
        study_id=study.id,
        item_name="smFRET_Polymerase_Fidelity_Transition_Trace",
        quantitative_value=0.42,
        profile_category="Primary Profile",
        log2_fold_change=1.85,
        significance_score=0.98,
    )
    assert profile.id is not None
    assert profile.study_id == study.id
    assert profile.item_name == "smFRET_Polymerase_Fidelity_Transition_Trace"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="fret_efficiency_transition_delta",
        observed_value=0.42,
        z_score=2.85,
        p_value=0.001,
    )
    assert trace.id is not None
    assert trace.study_id == study.id

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.id == study.id

    studies = await repo.list_studies()
    assert len(studies) >= 1
