"""Tests for Phase 257: Autonomous In-Silico Nanopore Direct RNA Sequencing (dRNA-seq) Base Modification Decoding Engine Repo."""

import pytest
from database.repositories.nanopore_direct_rna_modifications_repo import NanoporeDirectRnaModificationsRepository


@pytest.mark.asyncio
async def test_nanopore_direct_rna_modifications_repository(db_session):
    repo = NanoporeDirectRnaModificationsRepository(db_session)

    study = await repo.create_study(
        name="Study_257_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="nanopore-direct-rna-modifications",
        m6a_modification_detection_accuracy_pct=98.6,
        polya_tail_length_resolution_nt=1.8,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 257 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_257_Verification"
    assert getattr(study, "m6a_modification_detection_accuracy_pct") == 98.6

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="SARS_CoV_2_Subgenomic_RNA_m6A_Epitranscriptome_Map",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "SARS_CoV_2_Subgenomic_RNA_m6A_Epitranscriptome_Map"

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
    assert fetched.name == "Study_257_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
