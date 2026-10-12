"""Tests for Phase 432: Autonomous Continuous Directed Evolution PACE (Phage-Assisted Continuous Evolution) Fitness Trajectory Modeler Repo."""

import pytest
from database.repositories.pace_directed_evolution_trajectory_repo import PaceDirectedEvolutionTrajectoryRepository


@pytest.mark.asyncio
async def test_pace_directed_evolution_trajectory_repository(db_session):
    repo = PaceDirectedEvolutionTrajectoryRepository(db_session)

    study = await repo.create_study(
        name="Study_432_Verification",
        target_specimen="Continuous Chemostat Lago Lagoon Phage Population",
        analytical_modality="pace-directed-evolution",
        selection_stringency_factor=4.85,
        mutational_drift_velocity_subs_per_hr=0.32,
        fitness_enrichment_trajectory_fold=84.0,
        lagoon_dilution_rate_vol_per_hr=2.1,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 432 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_432_Verification"
    assert study.selection_stringency_factor == 4.85

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Continuous_Lago_Lagoon_Clonal_Expansion",
        profile_category="Primary Step",
        quantitative_value=4.85,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Continuous_Lago_Lagoon_Clonal_Expansion"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="fitness_enrichment_trajectory_fold",
        observed_value=4.85,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 4.85

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_432_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
