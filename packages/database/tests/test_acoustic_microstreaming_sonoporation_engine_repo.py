"""Tests for Phase 564: Autonomous Acoustic Micro-Streaming Single-Cell Intracellular Delivery Sonoporation Engine Repo."""

import pytest
from database.repositories.acoustic_microstreaming_sonoporation_engine_repo import AcousticMicrostreamingSonoporationEngineRepository


@pytest.mark.asyncio
async def test_acoustic_microstreaming_sonoporation_engine_repository(db_session):
    repo = AcousticMicrostreamingSonoporationEngineRepository(db_session)

    study = await repo.create_study(
        name="Study_564_Verification",
        target_specimen="Suspended Human CD34+ Hematopoietic Stem Cells and Phospholipid Microbubbles subjected to 1-MHz Focused Acoustic Waves",
        analytical_modality="acoustic-microstreaming-sonoporation",
        intracellular_delivery_efficiency_pct=92.4,
        cell_membrane_resealing_time_seconds=38.0,
        acoustic_cavitation_shear_stress_kpa=18.5,
        post_sonoporation_cell_viability_pct=94.8,
        confidence_score=0.996,
        status="completed",
        summary_report="Phase 564 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_564_Verification"
    assert study.intracellular_delivery_efficiency_pct == 92.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Transient_Pore_Microstreaming_Cavitation_Zone",
        profile_category="Primary Step",
        quantitative_value=92.4,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Transient_Pore_Microstreaming_Cavitation_Zone"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="intracellular_delivery_efficiency_pct",
        observed_value=92.4,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 92.4

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_564_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
