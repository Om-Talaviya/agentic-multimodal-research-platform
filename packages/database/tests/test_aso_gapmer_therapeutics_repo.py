"""Tests for Phase 193: Antisense Oligonucleotide RNase-H Cleavage & Gapmer Engine Repo."""

import pytest
from database.repositories.aso_gapmer_therapeutics_repo import ASOGapmerTherapeuticsRepository


@pytest.mark.asyncio
async def test_aso_gapmer_therapeutics_repository(db_session):
    repo = ASOGapmerTherapeuticsRepository(db_session)

    study = await repo.create_study(
        name="Study_193_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="Antisense Oligonucleotide Gapmer",
        rnase_h_cleavage_velocity_min=8.42,
        target_knockdown_percent=94.8,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 193 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_193_Verification"
    assert getattr(study, "rnase_h_cleavage_velocity_min") == 8.42

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="5-10-5 LNA-PS Gapmer [Cleavage Rate k_cat = 8.42 min-1]",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "5-10-5 LNA-PS Gapmer [Cleavage Rate k_cat = 8.42 min-1]"

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
    assert fetched.name == "Study_193_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
