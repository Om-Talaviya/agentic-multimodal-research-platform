"""Tests for Phase 418: Autonomous Cryo-ET High-Density Subtomogram Microtubule Protofilament & Motor Protein Stepping Tracker Repo."""

import pytest
from database.repositories.subtomogram_microtubule_stepping_repo import SubtomogramMicrotubuleSteppingRepository


@pytest.mark.asyncio
async def test_subtomogram_microtubule_stepping_repository(db_session):
    repo = SubtomogramMicrotubuleSteppingRepository(db_session)

    study = await repo.create_study(
        name="Study_418_Verification",
        target_specimen="Axonemal 13-Protofilament Microtubule with Kinesin-1 Dimers",
        analytical_modality="subtomogram-microtubule",
        subtomogram_resolution_angstrom=3.85,
        motor_step_size_nm=8.12,
        protofilament_twist_angle_deg=0.28,
        stepping_dwell_time_ms=18.5,
        confidence_score=0.989,
        status="completed",
        summary_report="Phase 418 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_418_Verification"
    assert study.subtomogram_resolution_angstrom == 3.85

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Kinesin_Motor_Domain_Protofilament_Lattice",
        profile_category="Primary Step",
        quantitative_value=3.85,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Kinesin_Motor_Domain_Protofilament_Lattice"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="subtomogram_resolution_angstrom",
        observed_value=3.85,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 3.85

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_418_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
