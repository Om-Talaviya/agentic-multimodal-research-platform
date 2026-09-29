"""Tests for Phase 271: Autonomous Multi-Organ Microphysiological Organ-on-a-Chip Multi-Plexed Biosensor Stream Engine Repo."""

import pytest
from database.repositories.microphysiological_organ_chip_sensors_repo import MicrophysiologicalOrganChipSensorsRepository


@pytest.mark.asyncio
async def test_microphysiological_organ_chip_sensors_repository(db_session):
    repo = MicrophysiologicalOrganChipSensorsRepository(db_session)

    study = await repo.create_study(
        name="Study_271_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="microphysiological-organ-chip-sensors",
        barrier_integrity_teer_ohm_cm2=1850.0,
        microfluidic_shear_stress_dyne_cm2=2.5,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 271 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_271_Verification"
    assert getattr(study, "barrier_integrity_teer_ohm_cm2") == 1850.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Blood_Brain_Barrier_Microvascular_TEER_Telemetry",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Blood_Brain_Barrier_Microvascular_TEER_Telemetry"

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
    assert fetched.name == "Study_271_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
