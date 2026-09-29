"""Tests for Phase 295: Autonomous Cryo-Electron Tomography (Cryo-ET) In-Situ Subtomogram Filament Tracing Simulator Repo."""

import pytest
from database.repositories.cryoet_insitu_filament_tracing_repo import CryoetInsituFilamentTracingRepository


@pytest.mark.asyncio
async def test_cryoet_insitu_filament_tracing_repository(db_session):
    repo = CryoetInsituFilamentTracingRepository(db_session)

    study = await repo.create_study(
        name="Study_295_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="cryoet-insitu-filament-tracing",
        filament_tracing_continuity_f1_score=95.8,
        macromolecular_crowding_volume_fraction_pct=34.2,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 295 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_295_Verification"
    assert getattr(study, "filament_tracing_continuity_f1_score") == 95.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Neuronal_Synapse_Actin_Cytoskeleton_Tomogram_Trace",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Neuronal_Synapse_Actin_Cytoskeleton_Tomogram_Trace"

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
    assert fetched.name == "Study_295_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
