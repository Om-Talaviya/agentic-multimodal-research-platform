"""Tests for Phase 544: Autonomous Integrated Cryo-CLEM High-Precision 3D Sub-Diffraction Nanoscale Fiducial Correlator Repo."""

import pytest
from database.repositories.cryo_correlative_light_electron_tomography_clem_repo import CryoCorrelativeLightElectronTomographyClemRepository


@pytest.mark.asyncio
async def test_cryo_correlative_light_electron_tomography_clem_repository(db_session):
    repo = CryoCorrelativeLightElectronTomographyClemRepository(db_session)

    study = await repo.create_study(
        name="Study_544_Verification",
        target_specimen="Cryo-Vitrified Neuronal Cultured Grid with Tetraspeck Fluorescent Nanobeads and Sub-10nm Gold Fiducials",
        analytical_modality="cryo-clem-fiducial-correlation",
        cross_modality_3d_registration_precision_nm=12.2,
        cryo_fluorescence_signal_to_background_ratio=48.5,
        cryo_fib_milling_target_accuracy_nm=24.0,
        subtomogram_correlation_coefficient=0.925,
        confidence_score=0.996,
        status="completed",
        summary_report="Phase 544 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_544_Verification"
    assert study.cross_modality_3d_registration_precision_nm == 12.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Super_Resolved_Fluorophore_Gold_Fiducial_Pair",
        profile_category="Primary Step",
        quantitative_value=12.2,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Super_Resolved_Fluorophore_Gold_Fiducial_Pair"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="cross_modality_3d_registration_precision_nm",
        observed_value=12.2,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 12.2

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_544_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
