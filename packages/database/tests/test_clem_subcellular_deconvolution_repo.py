"""Tests for Phase 372: Autonomous Correlative Light and Electron Microscopy (CLEM) Subcellular 3D Super-Resolution Deconvolver Repo."""

import pytest
from database.repositories.clem_subcellular_deconvolution_repo import ClemSubcellularDeconvolutionRepository


@pytest.mark.asyncio
async def test_clem_subcellular_deconvolution_repository(db_session):
    repo = ClemSubcellularDeconvolutionRepository(db_session)

    study = await repo.create_study(
        name="Study_372_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="clem-subcellular-deconvolution",
        correlative_fiducial_registration_accuracy_nm=3.8,
        subcellular_organelle_segmentation_dice_score=94.6,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 372 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_372_Verification"
    assert getattr(study, "correlative_fiducial_registration_accuracy_nm") == 3.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Mitochondrial_Cristae_Cryo_CLEM_Registration_Matrix",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Mitochondrial_Cristae_Cryo_CLEM_Registration_Matrix"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="Sensitivity & Recovery Rate",
        observed_value=0.984,
        z_score=2.85,
        p_value=0.00012,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.984

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_372_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
