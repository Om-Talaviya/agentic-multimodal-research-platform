"""Tests for Phase 569: Autonomous In-Situ Cryo-Correlative Super-Resolution Cryo-Fluorescence & Cryo-ET Single-Molecule Spatial Registration Engine repository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.super_resolution_cryo_fluorescence_correlator_repo import SuperResolutionCryoFluorescenceCorrelatorRepository


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
async def test_super_resolution_cryo_fluorescence_correlator_repository(async_session: AsyncSession):
    repo = SuperResolutionCryoFluorescenceCorrelatorRepository(async_session)

    study = await repo.create_study(
        name="Autonomous In-Situ Cryo-Correlative Super-Resolution Cryo-Fluorescence & Cryo-ET Single-Molecule Spatial Registration Engine Benchmark",
        target_specimen="Vitrified Mammalian HeLa Lamella with Cryo-Photoswitchable mEos4b Fluorophores and Gold Nanoparticle Fiducials",
        analytical_modality="cryo-super-resolution-registration",
        fiducial_registration_precision_nm=4.8,
        photobleaching_threshold_flux_kw_cm2=12.5,
        localization_confidence_score=0.985,
        cryo_optical_drift_variance_nm2=1.25,
        confidence_score=0.996,
        status="completed",
        summary_report="Automated validation benchmark passed successfully.",
    )
    assert study.id is not None
    assert study.name == "Autonomous In-Situ Cryo-Correlative Super-Resolution Cryo-Fluorescence & Cryo-ET Single-Molecule Spatial Registration Engine Benchmark"
    assert study.fiducial_registration_precision_nm == 4.8
    assert study.confidence_score == 0.996

    profile = await repo.add_item_profile(
        study_id=study.id,
        item_name="Cryo_Fluorescence_Correlated_Centroid_Locus",
        quantitative_value=4.8,
        profile_category="Primary Profile",
        log2_fold_change=1.85,
        significance_score=0.98,
    )
    assert profile.id is not None
    assert profile.study_id == study.id
    assert profile.item_name == "Cryo_Fluorescence_Correlated_Centroid_Locus"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="fiducial_registration_precision_nm",
        observed_value=4.8,
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
