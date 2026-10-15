"""Tests for Phase 543: Autonomous Biomimetic Neuromorphic Optoelectronic Synapse Photo-Memristive Plasticity Forecaster Repo."""

import pytest
from database.repositories.neuromorphic_optogenetic_synaptic_emulator_repo import NeuromorphicOptogeneticSynapticEmulatorRepository


@pytest.mark.asyncio
async def test_neuromorphic_optogenetic_synaptic_emulator_repository(db_session):
    repo = NeuromorphicOptogeneticSynapticEmulatorRepository(db_session)

    study = await repo.create_study(
        name="Study_543_Verification",
        target_specimen="2D Transition Metal Dichalcogenide (MoS2) / Perovskite Heterostructure Optoelectronic Synaptic Memristor",
        analytical_modality="optoelectronic-synapse-plasticity",
        paired_pulse_facilitation_ppf_index_pct=168.0,
        photo_induced_potentiation_energy_per_spike_fj=45.0,
        non_volatile_memory_retention_days=120.0,
        linear_weight_update_dynamic_range=4.8,
        confidence_score=0.994,
        status="completed",
        summary_report="Phase 543 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_543_Verification"
    assert study.paired_pulse_facilitation_ppf_index_pct == 168.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Optical_Spike_Induced_Photocarrier_Trapping_Trace",
        profile_category="Primary Step",
        quantitative_value=168.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Optical_Spike_Induced_Photocarrier_Trapping_Trace"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="paired_pulse_facilitation_ppf_index_pct",
        observed_value=168.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 168.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_543_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
