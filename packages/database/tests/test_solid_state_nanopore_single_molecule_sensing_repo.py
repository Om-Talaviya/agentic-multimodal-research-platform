"""Tests for Phase 417: Autonomous Solid-State Silicon Nitride Nanopore Single-Molecule Protein Translocation Engine Repo."""

import pytest
from database.repositories.solid_state_nanopore_single_molecule_sensing_repo import SolidStateNanoporeSensingRepository


@pytest.mark.asyncio
async def test_solid_state_nanopore_single_molecule_sensing_repository(db_session):
    repo = SolidStateNanoporeSensingRepository(db_session)

    study = await repo.create_study(
        name="Study_417_Verification",
        target_specimen="Conformationally Stretched Native Protein Translocation Through Sub-5nm SiNx Nanopore",
        analytical_modality="solid-state-nanopore",
        translocation_dwell_time_us=245.0,
        fractional_current_blockade_ratio=0.785,
        nanopore_diameter_nm=3.8,
        capture_frequency_events_per_s=18.5,
        confidence_score=0.988,
        status="completed",
        summary_report="Phase 417 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_417_Verification"
    assert study.translocation_dwell_time_us == 245.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Single_Molecule_Ionic_Current_Blockade_Event",
        profile_category="Primary Step",
        quantitative_value=245.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Single_Molecule_Ionic_Current_Blockade_Event"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="translocation_dwell_time_us",
        observed_value=245.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 245.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_417_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
