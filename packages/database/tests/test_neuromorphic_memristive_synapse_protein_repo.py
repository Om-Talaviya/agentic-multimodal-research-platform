"""Tests for Phase 521: Autonomous Biomolecular Protein Nanofiber Memristive Synaptic Weight Plasticity Forecaster Repo."""

import pytest
from database.repositories.neuromorphic_memristive_synapse_protein_repo import NeuromorphicMemristiveSynapseProteinRepository


@pytest.mark.asyncio
async def test_neuromorphic_memristive_synapse_protein_repository(db_session):
    repo = NeuromorphicMemristiveSynapseProteinRepository(db_session)

    study = await repo.create_study(
        name="Study_521_Verification",
        target_specimen="Crossbar Array of Self-Assembled Amyloid-beta / Ferritin Bio-Nanowires sandwiched between Pt/Au Electrodes",
        analytical_modality="biomolecular-memristor-plasticity",
        conductance_switching_on_off_ratio=185.0,
        spike_timing_dependent_plasticity_stdp_tau_ms=24.5,
        analog_conductance_states_count=64.0,
        endurance_switching_cycles=50000.0,
        confidence_score=0.992,
        status="completed",
        summary_report="Phase 521 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_521_Verification"
    assert study.conductance_switching_on_off_ratio == 185.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Redox_Conductive_Filament_Formation_Dissolution",
        profile_category="Primary Step",
        quantitative_value=185.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Redox_Conductive_Filament_Formation_Dissolution"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="conductance_switching_on_off_ratio",
        observed_value=185.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 185.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_521_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
