"""Tests for Phase 574: Autonomous Engineered Probiotic Gastrointestinal In-Vivo Biosurveillance & Colitis Biomarker Logic Gate Engine repository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.engineered_probiotic_in_vivo_biosurveillance_repo import EngineeredProbioticInVivoBiosurveillanceRepository


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
async def test_engineered_probiotic_in_vivo_biosurveillance_repository(async_session: AsyncSession):
    repo = EngineeredProbioticInVivoBiosurveillanceRepository(async_session)

    study = await repo.create_study(
        name="Autonomous Engineered Probiotic Gastrointestinal In-Vivo Biosurveillance & Colitis Biomarker Logic Gate Engine Benchmark",
        target_specimen="Engineered Escherichia coli Nissle 1917 Dual-Input Nitric Oxide and Tetrathionate Responsive Memory Circuit",
        analytical_modality="probiotic-in-vivo-biosurveillance",
        calprotectin_induction_fold_change=16.4,
        genetic_circuit_retention_stability=0.985,
        gut_colonization_density_cfu_g=450000000.0,
        false_positive_activation_rate=0.008,
        confidence_score=0.996,
        status="completed",
        summary_report="Automated validation benchmark passed successfully.",
    )
    assert study.id is not None
    assert study.name == "Autonomous Engineered Probiotic Gastrointestinal In-Vivo Biosurveillance & Colitis Biomarker Logic Gate Engine Benchmark"
    assert study.calprotectin_induction_fold_change == 16.4
    assert study.confidence_score == 0.996

    profile = await repo.add_item_profile(
        study_id=study.id,
        item_name="Probiotic_Biomarker_Surveillance_Gating_State",
        quantitative_value=16.4,
        profile_category="Primary Profile",
        log2_fold_change=1.85,
        significance_score=0.98,
    )
    assert profile.id is not None
    assert profile.study_id == study.id
    assert profile.item_name == "Probiotic_Biomarker_Surveillance_Gating_State"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="calprotectin_induction_fold_change",
        observed_value=16.4,
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
