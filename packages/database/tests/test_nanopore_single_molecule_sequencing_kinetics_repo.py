"""Tests for Phase 526: Autonomous Solid-State Nanopore Polymerase-Guided DNA Sequencing Kinetics Forecaster Repo."""

import pytest
from database.repositories.nanopore_single_molecule_sequencing_kinetics_repo import NanoporeSingleMoleculeSequencingKineticsRepository


@pytest.mark.asyncio
async def test_nanopore_single_molecule_sequencing_kinetics_repository(db_session):
    repo = NanoporeSingleMoleculeSequencingKineticsRepository(db_session)

    study = await repo.create_study(
        name="Study_526_Verification",
        target_specimen="Phi29 DNA Polymerase Coupled to Sub-2nm Si3N4 Solid-State Nanopore with Fluorescent dNTP Analogues",
        analytical_modality="nanopore-sequencing-kinetics",
        nucleotide_incorporation_dwell_time_ms=18.5,
        polymerase_processivity_base_pairs=2850.0,
        ionic_current_blockade_ratio=0.76,
        sequencing_raw_error_rate_pct=1.42,
        confidence_score=0.995,
        status="completed",
        summary_report="Phase 526 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_526_Verification"
    assert study.nucleotide_incorporation_dwell_time_ms == 18.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Single_Nucleotide_Translocation_Ionic_Current_Step",
        profile_category="Primary Step",
        quantitative_value=18.5,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Single_Nucleotide_Translocation_Ionic_Current_Step"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="nucleotide_incorporation_dwell_time_ms",
        observed_value=18.5,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 18.5

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_526_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
