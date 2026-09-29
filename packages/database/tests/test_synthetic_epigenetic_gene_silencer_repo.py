"""Tests for Phase 323: Autonomous CRISPR-dCas9 Directed Histone Methylation & DNA Methyltransferase Hit-and-Run Epigenetic Silencer Repo."""

import pytest
from database.repositories.synthetic_epigenetic_gene_silencer_repo import SyntheticEpigeneticGeneSilencerRepository


@pytest.mark.asyncio
async def test_synthetic_epigenetic_gene_silencer_repository(db_session):
    repo = SyntheticEpigeneticGeneSilencerRepository(db_session)

    study = await repo.create_study(
        name="Study_323_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="synthetic-epigenetic-silencer",
        durable_target_silencing_suppression_pct=98.7,
        epigenetic_memory_half_life_cell_divisions=85.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 323 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_323_Verification"
    assert getattr(study, "durable_target_silencing_suppression_pct") == 98.7

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="PCSK9_Targeted_Hit_and_Run_Epigenetic_Silencing_Construct",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "PCSK9_Targeted_Hit_and_Run_Epigenetic_Silencing_Construct"

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
    assert fetched.name == "Study_323_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
