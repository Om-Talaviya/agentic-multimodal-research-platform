"""Tests for Phase 463: Autonomous Neural Organoid Spontaneous Synchronous Bursting & Functional Connectivity Grapher Repo."""

import pytest
from database.repositories.neural_organoid_bursting_connectivity_repo import NeuralOrganoidBurstingConnectivityRepository


@pytest.mark.asyncio
async def test_neural_organoid_bursting_connectivity_repository(db_session):
    repo = NeuralOrganoidBurstingConnectivityRepository(db_session)

    study = await repo.create_study(
        name="Study_463_Verification",
        target_specimen="6-Month Human Cerebral Cortical Organoid on 4096-Channel CMOS High-Density MEA",
        analytical_modality="organoid-neural-connectivity",
        synchronous_network_burst_rate_hz=0.35,
        graph_small_world_clustering_coefficient=0.785,
        cross_correlation_functional_connectivity_density=0.842,
        shannon_entropy_burst_complexity=3.42,
        confidence_score=0.992,
        status="completed",
        summary_report="Phase 463 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_463_Verification"
    assert study.synchronous_network_burst_rate_hz == 0.35

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="High_Density_MEA_Global_Synchronous_Burst_Wave",
        profile_category="Primary Step",
        quantitative_value=0.35,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "High_Density_MEA_Global_Synchronous_Burst_Wave"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="synchronous_network_burst_rate_hz",
        observed_value=0.35,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.35

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_463_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
