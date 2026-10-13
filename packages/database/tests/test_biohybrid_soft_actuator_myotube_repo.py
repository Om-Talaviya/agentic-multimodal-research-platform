"""Tests for Phase 457: Autonomous Biohybrid Cybernetic Soft Actuator Myotube Electromechanical Force Forecaster Repo."""

import pytest
from database.repositories.biohybrid_soft_actuator_myotube_repo import BiohybridSoftActuatorMyotubeRepository


@pytest.mark.asyncio
async def test_biohybrid_soft_actuator_myotube_repository(db_session):
    repo = BiohybridSoftActuatorMyotubeRepository(db_session)

    study = await repo.create_study(
        name="Study_457_Verification",
        target_specimen="3D Bioprinted Optogenetic C2C12 Skeletal Myotube Cantilever on Flexible Hydrogel Skeleton",
        analytical_modality="biohybrid-actuator-mechanics",
        active_contractile_force_micro_newtons=285.0,
        twitch_to_tetanus_force_ratio=0.34,
        cyclic_fatigue_endurance_cycles=12500.0,
        electromechanical_coupling_efficiency=0.912,
        confidence_score=0.99,
        status="completed",
        summary_report="Phase 457 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_457_Verification"
    assert study.active_contractile_force_micro_newtons == 285.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Myotube_Optogenetic_Tetanic_Contraction_Spike",
        profile_category="Primary Step",
        quantitative_value=285.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Myotube_Optogenetic_Tetanic_Contraction_Spike"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="active_contractile_force_micro_newtons",
        observed_value=285.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 285.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_457_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
