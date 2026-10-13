"""Tests for Phase 466: Autonomous Optogenetic Rheotaxis Bacterial Micro-Swarm Bio-Convective Flow Modeler Repo."""

import pytest
from database.repositories.optogenetic_rheotaxis_micro_swarm_repo import OptogeneticRheotaxisMicroSwarmRepository


@pytest.mark.asyncio
async def test_optogenetic_rheotaxis_micro_swarm_repository(db_session):
    repo = OptogeneticRheotaxisMicroSwarmRepository(db_session)

    study = await repo.create_study(
        name="Study_466_Verification",
        target_specimen="Engineered B. subtilis Swarm with Light-Gated Flagellar Torque Switch in Laminar Microfluidic Channel",
        analytical_modality="optogenetic-rheotaxis-swarm",
        micro_swarm_upstream_drift_velocity_um_s=14.8,
        bioconvective_plume_wavelength_um=125.0,
        light_stimulated_phototactic_bias_ratio=3.42,
        vorticity_enstrophy_metric=0.925,
        confidence_score=0.989,
        status="completed",
        summary_report="Phase 466 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_466_Verification"
    assert study.micro_swarm_upstream_drift_velocity_um_s == 14.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Phototactic_Positive_Rheotaxis_Upstream_Streamline",
        profile_category="Primary Step",
        quantitative_value=14.8,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Phototactic_Positive_Rheotaxis_Upstream_Streamline"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="micro_swarm_upstream_drift_velocity_um_s",
        observed_value=14.8,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 14.8

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_466_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
