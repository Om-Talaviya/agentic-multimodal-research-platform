"""Tests for Phase 205: Synthetic Gene Circuit Toggle Switch & Stochastic Noise Forecaster Repo."""

import pytest
from database.repositories.synthetic_gene_toggle_switch_repo import SyntheticGeneToggleSwitchRepository


@pytest.mark.asyncio
async def test_synthetic_gene_toggle_switch_repository(db_session):
    repo = SyntheticGeneToggleSwitchRepository(db_session)

    study = await repo.create_study(
        name="Study_205_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="Synthetic Gene Toggle Switch",
        bistable_switching_threshold_molecules=145.0,
        stochastic_fano_factor_noise=1.84,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 205 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_205_Verification"
    assert getattr(study, "bistable_switching_threshold_molecules") == 145.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Repressor A Stable High State [LacI-GFP expression]",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Repressor A Stable High State [LacI-GFP expression]"

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
    assert fetched.name == "Study_205_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
