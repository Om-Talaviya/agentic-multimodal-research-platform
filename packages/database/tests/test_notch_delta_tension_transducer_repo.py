"""Tests for Phase 461: Autonomous Synthetic Morphogenetic Cell-Cell Contact Notch-Delta Mechanical Tension Transducer Repo."""

import pytest
from database.repositories.notch_delta_tension_transducer_repo import NotchDeltaTensionTransducerRepository


@pytest.mark.asyncio
async def test_notch_delta_tension_transducer_repository(db_session):
    repo = NotchDeltaTensionTransducerRepository(db_session)

    study = await repo.create_study(
        name="Study_461_Verification",
        target_specimen="Synthetic SynNotch Engineered Fibroblast Dual-Lattice Cell Sorting Array",
        analytical_modality="notch-delta-mechanotransduction",
        mechanical_pulling_force_pico_newtons=12.8,
        s2_s3_cleavage_transcription_activation_ratio=8.65,
        lateral_inhibition_bistability_index=0.925,
        boundary_sharpening_transition_width_cell_diameters=1.4,
        confidence_score=0.991,
        status="completed",
        summary_report="Phase 461 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_461_Verification"
    assert study.mechanical_pulling_force_pico_newtons == 12.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="E-Cadherin_Actomyosin_Pulling_Cleavage_Trigger",
        profile_category="Primary Step",
        quantitative_value=12.8,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "E-Cadherin_Actomyosin_Pulling_Cleavage_Trigger"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="mechanical_pulling_force_pico_newtons",
        observed_value=12.8,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 12.8

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_461_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
