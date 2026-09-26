"""Tests for Phase 195: CRISPR-Cas13 RNA-Targeting & Collateral Cleavage Suppressor Engine Repo."""

import pytest
from database.repositories.crispr_cas13_rna_targeting_repo import CRISPRCas13RNATargetingRepository


@pytest.mark.asyncio
async def test_crispr_cas13_rna_targeting_repository(db_session):
    repo = CRISPRCas13RNATargetingRepository(db_session)

    study = await repo.create_study(
        name="Study_195_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="CRISPR-Cas13 RNA Targeting",
        on_target_rna_knockdown_percent=96.4,
        collateral_rna_suppression_ratio=0.982,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 195 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_195_Verification"
    assert getattr(study, "on_target_rna_knockdown_percent") == 96.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Cas13d High-Fidelity Engineered Variant [HEPN N-term mutant]",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Cas13d High-Fidelity Engineered Variant [HEPN N-term mutant]"

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
    assert fetched.name == "Study_195_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
