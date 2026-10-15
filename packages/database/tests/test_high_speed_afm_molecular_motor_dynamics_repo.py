"""Tests for Phase 528: Autonomous High-Speed Atomic Force Microscopy (HS-AFM) Myosin Motor Stepping Real-Time Profiler Repo."""

import pytest
from database.repositories.high_speed_afm_molecular_motor_dynamics_repo import HighSpeedAfmMolecularMotorDynamicsRepository


@pytest.mark.asyncio
async def test_high_speed_afm_molecular_motor_dynamics_repository(db_session):
    repo = HighSpeedAfmMolecularMotorDynamicsRepository(db_session)

    study = await repo.create_study(
        name="Study_528_Verification",
        target_specimen="Single Native Myosin V Dimer stepping along Immobilized Actin Filament in Microfluidic HS-AFM Cell",
        analytical_modality="hs-afm-molecular-motor",
        hand_over_hand_step_distance_nm=36.2,
        power_stroke_lever_arm_rotation_deg=72.0,
        afm_cantilever_imaging_rate_fps=12.5,
        atp_limited_dwell_time_ms=42.0,
        confidence_score=0.996,
        status="completed",
        summary_report="Phase 528 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_528_Verification"
    assert study.hand_over_hand_step_distance_nm == 36.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Leading_Head_Actin_Binding_Power_Stroke_Frame",
        profile_category="Primary Step",
        quantitative_value=36.2,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Leading_Head_Actin_Binding_Power_Stroke_Frame"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="hand_over_hand_step_distance_nm",
        observed_value=36.2,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 36.2

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_528_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
