"""Tests for Phase 309: Autonomous Single-Cell Multiome ATAC-Seq & RNA Co-Assay Cis-Regulatory Network Inference Engine Repo."""

import pytest
from database.repositories.single_cell_multiome_cis_reg_network_repo import SingleCellMultiomeCisRegNetworkRepository


@pytest.mark.asyncio
async def test_single_cell_multiome_cis_reg_network_repository(db_session):
    repo = SingleCellMultiomeCisRegNetworkRepository(db_session)

    study = await repo.create_study(
        name="Study_309_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="single-cell-multiome-cis-reg",
        cis_regulatory_linkage_correlation_score=94.2,
        peak_to_gene_co_accessibility_r2=0.89,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 309 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_309_Verification"
    assert getattr(study, "cis_regulatory_linkage_correlation_score") == 94.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Cortical_Development_Chromatin_Transcription_Cis_Linkage_Map",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Cortical_Development_Chromatin_Transcription_Cis_Linkage_Map"

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
    assert fetched.name == "Study_309_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
