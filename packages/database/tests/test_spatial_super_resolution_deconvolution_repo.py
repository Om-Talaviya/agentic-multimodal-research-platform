"""Tests for Phase 299: Autonomous Spatial Transcriptomics Single-Molecule Spot Super-Resolution Diffusion Deconvolution Engine Repo."""

import pytest
from database.repositories.spatial_super_resolution_deconvolution_repo import SpatialSuperResolutionDeconvolutionRepository


@pytest.mark.asyncio
async def test_spatial_super_resolution_deconvolution_repository(db_session):
    repo = SpatialSuperResolutionDeconvolutionRepository(db_session)

    study = await repo.create_study(
        name="Study_299_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="spatial-super-resolution-deconvolution",
        super_resolution_spot_recovery_recall_pct=97.2,
        spatial_resolution_enhancement_factor=4.5,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 299 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_299_Verification"
    assert getattr(study, "super_resolution_spot_recovery_recall_pct") == 97.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Dense_FFPE_Tumor_Core_Sub_Diffraction_Deconvolution",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Dense_FFPE_Tumor_Core_Sub_Diffraction_Deconvolution"

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
    assert fetched.name == "Study_299_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
