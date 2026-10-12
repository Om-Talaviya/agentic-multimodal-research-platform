"""Tests for Phase 415: Autonomous Epitranscriptomic Direct RNA Nanopore Pseudouridine (Psi) & m6A Stoichiometry Profiler Repo."""

import pytest
from database.repositories.direct_rna_nanopore_pseudouridine_repo import DirectRnaNanoporePseudouridineRepository


@pytest.mark.asyncio
async def test_direct_rna_nanopore_pseudouridine_repository(db_session):
    repo = DirectRnaNanoporePseudouridineRepository(db_session)

    study = await repo.create_study(
        name="Study_415_Verification",
        target_specimen="Cellular Poly(A)+ Native mRNA Transcriptome",
        analytical_modality="direct-rna-nanopore",
        pseudouridine_stoichiometry_ratio=0.842,
        nanopore_dwell_time_shift_ms=14.8,
        ionic_current_deviation_pA=6.2,
        m6a_modification_frequency=0.765,
        confidence_score=0.987,
        status="completed",
        summary_report="Phase 415 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_415_Verification"
    assert study.pseudouridine_stoichiometry_ratio == 0.842

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Native_mRNA_Nanopore_Ionic_Current_Trace",
        profile_category="Primary Step",
        quantitative_value=0.842,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Native_mRNA_Nanopore_Ionic_Current_Trace"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="pseudouridine_stoichiometry_ratio",
        observed_value=0.842,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.842

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_415_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
