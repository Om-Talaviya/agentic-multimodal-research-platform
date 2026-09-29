"""Tests for Phase 336: Autonomous Direct-RNA Nanopore Sequencing Base Modification & m6A/Pseudouridine Epitrancriptome Caller Repo."""

import pytest
from database.repositories.nanopore_epitranscriptome_caller_repo import NanoporeEpitranscriptomeCallerRepository


@pytest.mark.asyncio
async def test_nanopore_epitranscriptome_caller_repository(db_session):
    repo = NanoporeEpitranscriptomeCallerRepository(db_session)

    study = await repo.create_study(
        name="Study_336_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="nanopore-epitranscriptome",
        modification_calling_accuracy_auroc=0.982,
        stoichiometric_quantification_precision_pct=96.4,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 336 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_336_Verification"
    assert getattr(study, "modification_calling_accuracy_auroc") == 0.982

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Neural_Stem_Cell_m6A_DRACH_Motif_Direct_RNA_Nanopore_Scan",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Neural_Stem_Cell_m6A_DRACH_Motif_Direct_RNA_Nanopore_Scan"

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
    assert fetched.name == "Study_336_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
