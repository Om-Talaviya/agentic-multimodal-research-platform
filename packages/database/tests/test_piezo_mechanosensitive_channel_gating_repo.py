"""Tests for Phase 494: Autonomous Mechanosensitive Ion Channel PIEZO1 Gating & Membrane Tension Indentation Engine Repo."""

import pytest
from database.repositories.piezo_mechanosensitive_channel_gating_repo import PiezoMechanosensitiveChannelGatingRepository


@pytest.mark.asyncio
async def test_piezo_mechanosensitive_channel_gating_repository(db_session):
    repo = PiezoMechanosensitiveChannelGatingRepository(db_session)

    study = await repo.create_study(
        name="Study_494_Verification",
        target_specimen="High-Speed Pressure Clamped HEK293 Cell expressing Human PIEZO1 Trimeric Propeller Blades",
        analytical_modality="piezo-mechanosensitive-gating",
        half_maximal_activation_tension_mN_per_m=2.85,
        channel_open_probability_p_open=0.945,
        single_channel_conductance_pS=29.5,
        mechanical_inactivation_tau_ms=16.2,
        confidence_score=0.994,
        status="completed",
        summary_report="Phase 494 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_494_Verification"
    assert study.half_maximal_activation_tension_mN_per_m == 2.85

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Trimeric_Propeller_Blade_Membrane_Dome_Flattening",
        profile_category="Primary Step",
        quantitative_value=2.85,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Trimeric_Propeller_Blade_Membrane_Dome_Flattening"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="half_maximal_activation_tension_mN_per_m",
        observed_value=2.85,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 2.85

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_494_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
