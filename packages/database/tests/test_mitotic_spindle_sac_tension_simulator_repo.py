"""Tests for Phase 452: Autonomous Microtubule Spindle Assembly Checkpoint (SAC) Mitotic Tension Kinetic Simulator Repo."""

import pytest
from database.repositories.mitotic_spindle_sac_tension_simulator_repo import MitoticSpindleSacTensionRepository


@pytest.mark.asyncio
async def test_mitotic_spindle_sac_tension_simulator_repository(db_session):
    repo = MitoticSpindleSacTensionRepository(db_session)

    study = await repo.create_study(
        name="Study_452_Verification",
        target_specimen="Bipolar Mitotic Kinetochore-Microtubule Interface with Mad2/BubR1 Checkpoint Sensor",
        analytical_modality="spindle-assembly-sac-kinetics",
        kinetochore_tension_pico_newtons=38.5,
        mad2_activation_rate_constant_s_inv=0.045,
        anaphase_onset_delay_minutes=18.2,
        spindle_bipolar_alignment_coherence=0.965,
        confidence_score=0.988,
        status="completed",
        summary_report="Phase 452 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_452_Verification"
    assert study.kinetochore_tension_pico_newtons == 38.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Kinetochore_Microtubule_Attachment_Stability",
        profile_category="Primary Step",
        quantitative_value=38.5,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Kinetochore_Microtubule_Attachment_Stability"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="kinetochore_tension_pico_newtons",
        observed_value=38.5,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 38.5

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_452_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
