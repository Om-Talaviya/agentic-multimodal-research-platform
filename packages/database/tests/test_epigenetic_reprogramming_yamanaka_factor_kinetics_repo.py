"""Tests for Phase 546: Autonomous Stochastic Pioneer Transcription Factor Yamanaka Reprogramming Trajectory Predictor Repo."""

import pytest
from database.repositories.epigenetic_reprogramming_yamanaka_factor_kinetics_repo import EpigeneticReprogrammingYamanakaFactorKineticsRepository


@pytest.mark.asyncio
async def test_epigenetic_reprogramming_yamanaka_factor_kinetics_repository(db_session):
    repo = EpigeneticReprogrammingYamanakaFactorKineticsRepository(db_session)

    study = await repo.create_study(
        name="Study_546_Verification",
        target_specimen="Single-Cell Doxycycline-Inducible OSKM Human Dermal Fibroblasts tracked across 21 Days",
        analytical_modality="yamanaka-reprogramming-kinetics",
        fully_reprogrammed_naive_pluripotency_rate_pct=8.5,
        oct4_sox2_pioneer_chromatin_dwell_time_s=32.0,
        dna_methylation_clock_reversal_years=45.0,
        trajectory_waddington_barrier_crossing_prob=0.14,
        confidence_score=0.995,
        status="completed",
        summary_report="Phase 546 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_546_Verification"
    assert study.fully_reprogrammed_naive_pluripotency_rate_pct == 8.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Pluripotency_Super_Enhancer_Pioneer_Nucleation",
        profile_category="Primary Step",
        quantitative_value=8.5,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Pluripotency_Super_Enhancer_Pioneer_Nucleation"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="fully_reprogrammed_naive_pluripotency_rate_pct",
        observed_value=8.5,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 8.5

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_546_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
