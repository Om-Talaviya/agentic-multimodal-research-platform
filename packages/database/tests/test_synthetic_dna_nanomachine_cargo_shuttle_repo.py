"""Tests for Phase 523: Autonomous Autonomous DNA Nanomachine Cargo Transport Track Walker & Dynamic Shuttle Repo."""

import pytest
from database.repositories.synthetic_dna_nanomachine_cargo_shuttle_repo import SyntheticDnaNanomachineCargoShuttleRepository


@pytest.mark.asyncio
async def test_synthetic_dna_nanomachine_cargo_shuttle_repository(db_session):
    repo = SyntheticDnaNanomachineCargoShuttleRepository(db_session)

    study = await repo.create_study(
        name="Study_523_Verification",
        target_specimen="Scaffolded DNA Origami 2D Origami Track with Autonomous Kinesin-Mimic Fuel-Fueled DNA Bipedal Walker",
        analytical_modality="dna-nanomachine-shuttle",
        walker_directional_velocity_nm_per_min=18.0,
        fuel_strand_consumption_efficiency=0.965,
        molecular_cargo_handover_fidelity_pct=98.4,
        continuous_processive_stepping_distance_nm=320.0,
        confidence_score=0.993,
        status="completed",
        summary_report="Phase 523 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_523_Verification"
    assert study.walker_directional_velocity_nm_per_min == 18.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Toehold_Mediated_Branch_Migration_Stepping_Leg",
        profile_category="Primary Step",
        quantitative_value=18.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Toehold_Mediated_Branch_Migration_Stepping_Leg"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="walker_directional_velocity_nm_per_min",
        observed_value=18.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 18.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_523_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
