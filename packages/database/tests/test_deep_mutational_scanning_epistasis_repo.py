"""Tests for Phase 424: Autonomous Deep Mutational Scanning (DMS) Variant Fitness & Thermostability Epistasis Forecaster Repo."""

import pytest
from database.repositories.deep_mutational_scanning_epistasis_repo import DeepMutationalScanningEpistasisRepository


@pytest.mark.asyncio
async def test_deep_mutational_scanning_epistasis_repository(db_session):
    repo = DeepMutationalScanningEpistasisRepository(db_session)

    study = await repo.create_study(
        name="Study_424_Verification",
        target_specimen="Beta-Lactamase All-Combinatorial Single/Double Point Mutants",
        analytical_modality="dms-epistasis",
        higher_order_epistasis_coefficient=0.385,
        relative_fitness_enrichment_ratio=2.45,
        delta_delta_g_unfolding_kcal=1.82,
        catalytic_efficiency_retention=0.924,
        confidence_score=0.989,
        status="completed",
        summary_report="Phase 424 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_424_Verification"
    assert study.higher_order_epistasis_coefficient == 0.385

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Combinatorial_Epistasis_Fitness_Landscape",
        profile_category="Primary Step",
        quantitative_value=0.385,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Combinatorial_Epistasis_Fitness_Landscape"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="higher_order_epistasis_coefficient",
        observed_value=0.385,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.385

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_424_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
