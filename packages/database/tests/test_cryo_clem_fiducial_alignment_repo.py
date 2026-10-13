"""Tests for Phase 460: Autonomous In-Situ Cryo-CLEM Fluorescent Target Correlation & Precision Fiducial Alignment Engine Repo."""

import pytest
from database.repositories.cryo_clem_fiducial_alignment_repo import CryoClemFiducialAlignmentRepository


@pytest.mark.asyncio
async def test_cryo_clem_fiducial_alignment_repository(db_session):
    repo = CryoClemFiducialAlignmentRepository(db_session)

    study = await repo.create_study(
        name="Study_460_Verification",
        target_specimen="Vitrified Primary Axon Growth Cone with Gold Nanoparticle Fiducials and GFP-Tagged Cargo",
        analytical_modality="cryo-clem-fiducial-alignment",
        coordinate_transformation_target_registration_error_nm=28.5,
        fiducial_triangulation_residual_angstrom=18.2,
        fluorescence_cryo_snr_decibels=24.6,
        target_feature_hit_probability=0.965,
        confidence_score=0.993,
        status="completed",
        summary_report="Phase 460 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_460_Verification"
    assert study.coordinate_transformation_target_registration_error_nm == 28.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Gold_Bead_Affine_Transformation_Triangulation",
        profile_category="Primary Step",
        quantitative_value=28.5,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Gold_Bead_Affine_Transformation_Triangulation"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="coordinate_transformation_target_registration_error_nm",
        observed_value=28.5,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 28.5

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_460_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
