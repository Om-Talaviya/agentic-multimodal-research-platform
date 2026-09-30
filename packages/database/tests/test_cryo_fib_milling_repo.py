"""Tests for Phase 414: Autonomous Cryo-FIB Milling & In-Situ Lamella Thickness Optimization Engine Repo."""

import pytest
from database.repositories.cryo_fib_milling_repo import CryoFibMillingRepository


@pytest.mark.asyncio
async def test_cryo_fib_milling_repository(db_session):
    repo = CryoFibMillingRepository(db_session)

    study = await repo.create_study(
        name="Study_414_Verification",
        target_specimen="Vitreous Cellular Cryo-Lamella",
        analytical_modality="cryo-fib-milling",
        in_situ_lamella_thickness_nm=112.5,
        curtaining_artifact_suppression_ratio=0.948,
        gallium_ion_beam_current_pA=30.0,
        vitreous_ice_preservation_score=0.982,
        confidence_score=0.988,
        status="completed",
        summary_report="Phase 414 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_414_Verification"
    assert study.in_situ_lamella_thickness_nm == 112.5
    assert study.curtaining_artifact_suppression_ratio == 0.948

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="In_Situ_Vitreous_Lamella_Thinning_Stage",
        profile_category="Primary Milling Step",
        quantitative_value=112.5,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "In_Situ_Vitreous_Lamella_Thinning_Stage"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="in_situ_lamella_thickness_nm",
        observed_value=112.5,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 112.5

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_414_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
