"""Tests for Phase 211: Autonomous Single-Cell Copy Number Variation (scCNV) & Chromosomal Aneuploidy Karyotyper Engine Repo."""

import pytest
from database.repositories.scrna_copy_number_karyotype_repo import ScRNACopyNumberKaryotypeRepository


@pytest.mark.asyncio
async def test_scrna_copy_number_karyotype_repository(db_session):
    repo = ScRNACopyNumberKaryotypeRepository(db_session)

    study = await repo.create_study(
        name="Study_211_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="scrna-copy-number-karyotype",
        aneuploidy_confidence_score=98.6,
        breakpoint_resolution_kb=125.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 211 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_211_Verification"
    assert getattr(study, "aneuploidy_confidence_score") == 98.6

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Glioblastoma_scRNA_Subclone_Chr7Gain_Chr10Loss",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Glioblastoma_scRNA_Subclone_Chr7Gain_Chr10Loss"

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
    assert fetched.name == "Study_211_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
