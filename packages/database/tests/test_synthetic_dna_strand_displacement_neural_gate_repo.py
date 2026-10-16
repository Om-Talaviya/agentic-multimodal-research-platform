"""Tests for Phase 570: Autonomous Synthetic DNA Strand Displacement (DSD) Molecular Neural Network Winner-Take-All Classifier Engine repository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.synthetic_dna_strand_displacement_neural_gate_repo import SyntheticDnaStrandDisplacementNeuralGateRepository


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
async def test_synthetic_dna_strand_displacement_neural_gate_repository(async_session: AsyncSession):
    repo = SyntheticDnaStrandDisplacementNeuralGateRepository(async_session)

    study = await repo.create_study(
        name="Autonomous Synthetic DNA Strand Displacement (DSD) Molecular Neural Network Winner-Take-All Classifier Engine Benchmark",
        target_specimen="Toehold-Mediated 4-Input 2-Class DNA Strand Displacement Reaction Network in Tris-Acetate-EDTA Buffer",
        analytical_modality="dsd-molecular-neural-classification",
        toehold_exchange_rate_constant_m_s=350000.0,
        signal_to_leakage_ratio=28.5,
        winner_take_all_convergence_time_s=185.0,
        decision_boundary_sharpness=0.965,
        confidence_score=0.997,
        status="completed",
        summary_report="Automated validation benchmark passed successfully.",
    )
    assert study.id is not None
    assert study.name == "Autonomous Synthetic DNA Strand Displacement (DSD) Molecular Neural Network Winner-Take-All Classifier Engine Benchmark"
    assert study.toehold_exchange_rate_constant_m_s == 350000.0
    assert study.confidence_score == 0.997

    profile = await repo.add_item_profile(
        study_id=study.id,
        item_name="DSD_Winner_Take_All_Equilibrium_State",
        quantitative_value=350000.0,
        profile_category="Primary Profile",
        log2_fold_change=1.85,
        significance_score=0.98,
    )
    assert profile.id is not None
    assert profile.study_id == study.id
    assert profile.item_name == "DSD_Winner_Take_All_Equilibrium_State"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="signal_to_leakage_ratio",
        observed_value=350000.0,
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
