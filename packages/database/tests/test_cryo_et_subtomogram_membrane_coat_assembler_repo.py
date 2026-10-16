"""Tests for Phase 575: Autonomous In-Situ Cryo-ET Subtomogram Averaging Clathrin & COP-II Vesicular Membrane Coat Symmetry Assembler repository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.cryo_et_subtomogram_membrane_coat_assembler_repo import CryoEtSubtomogramMembraneCoatAssemblerRepository


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
async def test_cryo_et_subtomogram_membrane_coat_assembler_repository(async_session: AsyncSession):
    repo = CryoEtSubtomogramMembraneCoatAssemblerRepository(async_session)

    study = await repo.create_study(
        name="Autonomous In-Situ Cryo-ET Subtomogram Averaging Clathrin & COP-II Vesicular Membrane Coat Symmetry Assembler Benchmark",
        target_specimen="Vitrified Saccharomyces cerevisiae Budding Vesicle Donor Sites with COP-II Polyhedral Lattice Outer Shell",
        analytical_modality="cryoet-subtomogram-coat-assembly",
        subtomogram_resolution_fsc0143_a=4.15,
        cage_polyhedral_symmetry_index=0.945,
        membrane_curvature_coupling_energy_kbt=24.8,
        angular_orientation_precision_deg=1.85,
        confidence_score=0.995,
        status="completed",
        summary_report="Automated validation benchmark passed successfully.",
    )
    assert study.id is not None
    assert study.name == "Autonomous In-Situ Cryo-ET Subtomogram Averaging Clathrin & COP-II Vesicular Membrane Coat Symmetry Assembler Benchmark"
    assert study.subtomogram_resolution_fsc0143_a == 4.15
    assert study.confidence_score == 0.995

    profile = await repo.add_item_profile(
        study_id=study.id,
        item_name="Subtomogram_Membrane_Coat_Lattice_Assembly",
        quantitative_value=4.15,
        profile_category="Primary Profile",
        log2_fold_change=1.85,
        significance_score=0.98,
    )
    assert profile.id is not None
    assert profile.study_id == study.id
    assert profile.item_name == "Subtomogram_Membrane_Coat_Lattice_Assembly"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="subtomogram_resolution_fsc0143_a",
        observed_value=4.15,
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
