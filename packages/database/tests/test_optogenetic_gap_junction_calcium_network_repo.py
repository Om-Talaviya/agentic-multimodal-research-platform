"""Tests for Phase 554: Autonomous Optogenetic Intercellular Gap Junction Coupling & Calcium Synchrony Network Forecaster Repo."""

import pytest
from database.repositories.optogenetic_gap_junction_calcium_network_repo import OptogeneticGapJunctionCalciumNetworkRepository


@pytest.mark.asyncio
async def test_optogenetic_gap_junction_calcium_network_repository(db_session):
    repo = OptogeneticGapJunctionCalciumNetworkRepository(db_session)

    study = await repo.create_study(
        name="Study_554_Verification",
        target_specimen="Confluent Monolayer of Human Induced Pluripotent Stem Cell-Derived Cardiomyocytes expressing Channelrhodopsin-2 and Connexin-43",
        analytical_modality="optogenetic-gap-junction-sync",
        calcium_wave_propagation_velocity_um_s=380.0,
        connexin43_gap_junction_conductance_ns=42.5,
        network_phase_synchronization_order_param=0.965,
        action_potential_duration_apd90_ms=310.0,
        confidence_score=0.996,
        status="completed",
        summary_report="Phase 554 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_554_Verification"
    assert study.calcium_wave_propagation_velocity_um_s == 380.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Intercellular_Syncytium_Conduction_Wavefront_Lattice",
        profile_category="Primary Step",
        quantitative_value=380.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Intercellular_Syncytium_Conduction_Wavefront_Lattice"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="calcium_wave_propagation_velocity_um_s",
        observed_value=380.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 380.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_554_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
