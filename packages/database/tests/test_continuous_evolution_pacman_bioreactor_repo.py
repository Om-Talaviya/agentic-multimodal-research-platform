"""Tests for Phase 326: Autonomous PACE (Phage-Assisted Continuous Evolution) Dynamic Turbidostat Selection Feedback Controller Repo."""

import pytest
from database.repositories.continuous_evolution_pacman_bioreactor_repo import ContinuousEvolutionPacmanBioreactorRepository


@pytest.mark.asyncio
async def test_continuous_evolution_pacman_bioreactor_repository(db_session):
    repo = ContinuousEvolutionPacmanBioreactorRepository(db_session)

    study = await repo.create_study(
        name="Study_326_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="continuous-evolution-pacman",
        evolved_enzyme_catalytic_efficiency_kcat_km_fold_improvement=185.0,
        evolution_cycle_generations_per_day=36.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 326 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_326_Verification"
    assert getattr(study, "evolved_enzyme_catalytic_efficiency_kcat_km_fold_improvement") == 185.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Polymerase_Unnatural_Base_Pair_Recognition_PACE_Turbidostat",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Polymerase_Unnatural_Base_Pair_Recognition_PACE_Turbidostat"

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
    assert fetched.name == "Study_326_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
