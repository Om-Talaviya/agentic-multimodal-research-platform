"""Tests for Phase 206: Single-Cell Multiome ATAC+GEX Peak-to-Gene Cis-Regulatory Engine Repo."""

import pytest
from database.repositories.multiome_atac_gex_cisreg_repo import MultiomeATACGEXCisRegRepository


@pytest.mark.asyncio
async def test_multiome_atac_gex_cisreg_repository(db_session):
    repo = MultiomeATACGEXCisRegRepository(db_session)

    study = await repo.create_study(
        name="Study_206_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="Multiome ATAC GEX Cis-Reg",
        peak_gene_correlation_pearson=0.842,
        transcription_factor_regulon_activity_auc=0.965,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 206 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_206_Verification"
    assert getattr(study, "peak_gene_correlation_pearson") == 0.842

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="High-Confidence Peak-to-Gene Link [chr11:5248231 -> HBB]",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "High-Confidence Peak-to-Gene Link [chr11:5248231 -> HBB]"

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
    assert fetched.name == "Study_206_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
