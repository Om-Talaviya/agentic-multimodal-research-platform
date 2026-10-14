"""Tests for Phase 474: Autonomous Subcellular Microtubule Kinesin-Dynein Tug-of-War Vesicle Transport Modeler Repo."""

import pytest
from database.repositories.kinesin_dynein_vesicle_transport_repo import KinesinDyneinVesicleTransportRepository


@pytest.mark.asyncio
async def test_kinesin_dynein_vesicle_transport_repository(db_session):
    repo = KinesinDyneinVesicleTransportRepository(db_session)

    study = await repo.create_study(
        name="Study_474_Verification",
        target_specimen="Vitrified Axonal Microtubule Filament with Dual Kinesin-1 and Cytoplasmic Dynein Vesicle Cargo",
        analytical_modality="kinesin-dynein-tug-of-war",
        anterograde_retrograde_velocity_ratio=1.42,
        motor_detachment_stall_force_pN=7.2,
        mean_run_length_processivity_um=3.85,
        tug_of_war_cooperative_coordination_index=0.915,
        confidence_score=0.993,
        status="completed",
        summary_report="Phase 474 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_474_Verification"
    assert study.anterograde_retrograde_velocity_ratio == 1.42

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Opposing_Motor_Ensemble_Stochastic_Tug_of_War",
        profile_category="Primary Step",
        quantitative_value=1.42,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Opposing_Motor_Ensemble_Stochastic_Tug_of_War"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="anterograde_retrograde_velocity_ratio",
        observed_value=1.42,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 1.42

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_474_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
