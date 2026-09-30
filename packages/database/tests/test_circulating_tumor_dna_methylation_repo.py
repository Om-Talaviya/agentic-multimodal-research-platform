"""Tests for Phase 402: Liquid Biopsy ctDNA Methylation & Tissue-of-Origin Deconvolver Repo."""

import pytest
from database.repositories.circulating_tumor_dna_methylation_repo import CirculatingTumorDnaMethylationRepository


@pytest.mark.asyncio
async def test_circulating_tumor_dna_methylation_repository(db_session):
    repo = CirculatingTumorDnaMethylationRepository(db_session)

    study = await repo.create_study(
        name="Study_402_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="liquid-biopsy-ctdna-methylation",
        tissue_of_origin_classification_accuracy_pct=96.8,
        ctdna_limit_of_detection_allele_fraction_ppm=8.5,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 402 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_402_Verification"
    assert getattr(study, "tissue_of_origin_classification_accuracy_pct") == 96.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Differentially_Methylated_CpG_Island_Signature_Colorectal",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Differentially_Methylated_CpG_Island_Signature_Colorectal"

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
    assert fetched.name == "Study_402_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
