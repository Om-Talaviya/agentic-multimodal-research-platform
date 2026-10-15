"""Tests for Phase 542: Autonomous Direct RNA Nanopore Sequencing Pseudouridine (Ψ) Chemical Stoichiometry Profiler Repo."""

import pytest
from database.repositories.direct_rna_pseudouridine_nanopore_sequencing_repo import DirectRnaPseudouridineNanoporeSequencingRepository


@pytest.mark.asyncio
async def test_direct_rna_pseudouridine_nanopore_sequencing_repository(db_session):
    repo = DirectRnaPseudouridineNanoporeSequencingRepository(db_session)

    study = await repo.create_study(
        name="Study_542_Verification",
        target_specimen="Native Human rRNA and mRNA Direct Oxford Nanopore Sequencing with CMC Chemical Adduct Validation",
        analytical_modality="direct-rna-pseudouridine-stoichiometry",
        pseudouridine_stoichiometry_detection_accuracy=0.978,
        ionic_current_dwell_shift_sigma=3.42,
        single_molecule_modification_calling_f1=0.965,
        low_abundance_transcript_coverage_depth=450.0,
        confidence_score=0.995,
        status="completed",
        summary_report="Phase 542 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_542_Verification"
    assert study.pseudouridine_stoichiometry_detection_accuracy == 0.978

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Pseudouridine_Blockade_Ionic_Current_Signature",
        profile_category="Primary Step",
        quantitative_value=0.978,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Pseudouridine_Blockade_Ionic_Current_Signature"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="pseudouridine_stoichiometry_detection_accuracy",
        observed_value=0.978,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.978

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_542_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
