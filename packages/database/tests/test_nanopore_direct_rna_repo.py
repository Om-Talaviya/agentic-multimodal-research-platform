"""Tests for Phase 189: Nanopore Direct RNA Sequencing & Epitranscriptomic Modification Mapper Repo."""

import pytest
from database.repositories.nanopore_direct_rna_repo import NanoporeDirectRNARepository


@pytest.mark.asyncio
async def test_nanopore_direct_rna_repository(db_session):
    repo = NanoporeDirectRNARepository(db_session)

    study = await repo.create_study(
        name="Study_189_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="Nanopore Direct RNA Epitranscriptomics",
        median_polya_tail_length_nt=145.2,
        epitranscriptomic_modification_stoichiometry=0.842,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 189 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_189_Verification"
    assert getattr(study, "median_polya_tail_length_nt") == 145.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="N6-Methyladenosine (m6A) DRACH Motif [chr19:45291]",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "N6-Methyladenosine (m6A) DRACH Motif [chr19:45291]"

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
    assert fetched.name == "Study_189_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
