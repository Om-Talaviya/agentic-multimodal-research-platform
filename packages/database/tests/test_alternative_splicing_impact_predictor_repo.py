"""Tests for Phase 343: Autonomous Whole-Transcriptome Alternative Splicing & Exon Skipping Functional Impact Predictor Repo."""

import pytest
from database.repositories.alternative_splicing_impact_predictor_repo import AlternativeSplicingImpactPredictorRepository


@pytest.mark.asyncio
async def test_alternative_splicing_impact_predictor_repository(db_session):
    repo = AlternativeSplicingImpactPredictorRepository(db_session)

    study = await repo.create_study(
        name="Study_343_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="alternative-splicing-impact",
        percent_spliced_in_psi_shift_delta_pct=72.0,
        nonsense_mediated_decay_evasion_probability_pct=94.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 343 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_343_Verification"
    assert getattr(study, "percent_spliced_in_psi_shift_delta_pct") == 72.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="SMN2_Exon_7_Inclusion_Splice_Switching_Oligonucleotide_Design",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "SMN2_Exon_7_Inclusion_Splice_Switching_Oligonucleotide_Design"

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
    assert fetched.name == "Study_343_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
