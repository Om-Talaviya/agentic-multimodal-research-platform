"""Tests for Phase 285: Autonomous Synthetic Minimal Yeast Chromosome (Sc2.0) loxPsym Site-Specific Recombination (SCRaMbLE) Simulator Repo."""

import pytest
from database.repositories.scramble_synthetic_chromosome_simulator_repo import ScrambleSyntheticChromosomeSimulatorRepository


@pytest.mark.asyncio
async def test_scramble_synthetic_chromosome_simulator_repository(db_session):
    repo = ScrambleSyntheticChromosomeSimulatorRepository(db_session)

    study = await repo.create_study(
        name="Study_285_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="scramble-synthetic-chromosome-simulator",
        scramble_recombination_fitness_prediction_score=97.2,
        viable_structural_variant_diversity_index=8.5,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 285 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_285_Verification"
    assert getattr(study, "scramble_recombination_fitness_prediction_score") == 97.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Yeast_SynIXR_Chromosome_SCRaMbLE_Evolution_Trajectory",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Yeast_SynIXR_Chromosome_SCRaMbLE_Evolution_Trajectory"

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
    assert fetched.name == "Study_285_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
