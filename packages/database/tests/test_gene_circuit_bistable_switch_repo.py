"""Tests for Phase 472: Autonomous Synthetic Gene Circuit Cross-Repression Epigenetic Bistable Switch Simulator Repo."""

import pytest
from database.repositories.gene_circuit_bistable_switch_repo import GeneCircuitBistableSwitchRepository


@pytest.mark.asyncio
async def test_gene_circuit_bistable_switch_repository(db_session):
    repo = GeneCircuitBistableSwitchRepository(db_session)

    study = await repo.create_study(
        name="Study_472_Verification",
        target_specimen="Synthetic LacI-TetR Mutual Inactivation Toggle Switch with Epigenetic DNA Methylation Memory",
        analytical_modality="gene-circuit-bistable-switch",
        bistable_hysteresis_basin_depth_au=4.85,
        stochastic_switching_barrier_height_kbT=18.2,
        state_transition_retention_half_life_hours=144.0,
        cooperative_hill_coefficient=2.85,
        confidence_score=0.991,
        status="completed",
        summary_report="Phase 472 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_472_Verification"
    assert study.bistable_hysteresis_basin_depth_au == 4.85

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Mutual_Repression_Attractor_Basin_Stability",
        profile_category="Primary Step",
        quantitative_value=4.85,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Mutual_Repression_Attractor_Basin_Stability"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="bistable_hysteresis_basin_depth_au",
        observed_value=4.85,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 4.85

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_472_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
