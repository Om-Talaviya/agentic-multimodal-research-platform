"""Tests for Phase 270: Autonomous Single-Molecule RNA Structural Transition FRET Kinetics & Riboswitch Dynamic Trajectory Engine Repo."""

import pytest
from database.repositories.smfret_riboswitch_kinetics_repo import SmfretRiboswitchKineticsRepository


@pytest.mark.asyncio
async def test_smfret_riboswitch_kinetics_repository(db_session):
    repo = SmfretRiboswitchKineticsRepository(db_session)

    study = await repo.create_study(
        name="Study_270_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="smfret-riboswitch-kinetics",
        smfret_kinetic_rate_kon_s_inv=14.8,
        conformational_state_fret_efficiency_delta=0.42,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 270 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_270_Verification"
    assert getattr(study, "smfret_kinetic_rate_kon_s_inv") == 14.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="SAM_I_Riboswitch_Aptamer_Domain_FRET_Trajectory",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "SAM_I_Riboswitch_Aptamer_Domain_FRET_Trajectory"

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
    assert fetched.name == "Study_270_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
