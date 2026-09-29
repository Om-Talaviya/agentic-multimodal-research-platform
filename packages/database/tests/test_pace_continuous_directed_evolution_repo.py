"""Tests for Phase 288: Autonomous Continuous Directed Protein Evolution (PACE) Phage Mutagenesis & Selection Velocity Engine Repo."""

import pytest
from database.repositories.pace_continuous_directed_evolution_repo import PaceContinuousDirectedEvolutionRepository


@pytest.mark.asyncio
async def test_pace_continuous_directed_evolution_repository(db_session):
    repo = PaceContinuousDirectedEvolutionRepository(db_session)

    study = await repo.create_study(
        name="Study_288_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="pace-continuous-directed-evolution",
        selection_velocity_generations_per_hour=4.8,
        evolved_variant_fitness_gain_fold=32.5,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 288 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_288_Verification"
    assert getattr(study, "selection_velocity_generations_per_hour") == 4.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="T7_RNA_Polymerase_Promoter_Recognition_PACE_Arc",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "T7_RNA_Polymerase_Promoter_Recognition_PACE_Arc"

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
    assert fetched.name == "Study_288_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
