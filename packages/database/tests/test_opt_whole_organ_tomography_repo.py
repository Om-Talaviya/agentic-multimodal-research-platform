"""Tests for Phase 367: Autonomous High-Resolution Optical Projection Tomography (OPT) Whole-Organ Cleared Tissue Reconstructor Repo."""

import pytest
from database.repositories.opt_whole_organ_tomography_repo import OptWholeOrganTomographyRepository


@pytest.mark.asyncio
async def test_opt_whole_organ_tomography_repository(db_session):
    repo = OptWholeOrganTomographyRepository(db_session)

    study = await repo.create_study(
        name="Study_367_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="opt-whole-organ-tomography",
        isotropic_spatial_voxel_resolution_microns=5.0,
        volumetric_reconstruction_ssim_index=0.965,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 367 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_367_Verification"
    assert getattr(study, "isotropic_spatial_voxel_resolution_microns") == 5.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Whole_Mouse_Pancreatic_Islet_Cell_3D_Volumetric_Map",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Whole_Mouse_Pancreatic_Islet_Cell_3D_Volumetric_Map"

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
    assert fetched.name == "Study_367_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
