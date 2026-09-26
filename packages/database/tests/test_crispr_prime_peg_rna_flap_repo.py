"""Tests for Phase 222: Autonomous CRISPR Prime Editing pegRNA Primer Binding Site (PBS) & Reverse Transcription Flap Kinetics Synthesizer Engine Repo."""

import pytest
from database.repositories.crispr_prime_peg_rna_flap_repo import CrisprPrimePegRnaFlapRepository


@pytest.mark.asyncio
async def test_crispr_prime_peg_rna_flap_repository(db_session):
    repo = CrisprPrimePegRnaFlapRepository(db_session)

    study = await repo.create_study(
        name="Study_222_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="crispr-prime-peg-rna-flap",
        prime_editing_efficiency_pct=78.4,
        indel_byproduct_ratio_pct=1.2,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 222 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_222_Verification"
    assert getattr(study, "prime_editing_efficiency_pct") == 78.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="HEK3_Site_Prime_pegRNA_PBS13_RTT15",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "HEK3_Site_Prime_pegRNA_PBS13_RTT15"

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
    assert fetched.name == "Study_222_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
