"""Tests for Phase 453: Autonomous Quantum Dots-Mediated Optoelectronic Neuromorphic Synaptic Potentiation Modeler Repo."""

import pytest
from database.repositories.quantum_dots_optoelectronic_synapse_repo import QuantumDotsOptoelectronicSynapseRepository


@pytest.mark.asyncio
async def test_quantum_dots_optoelectronic_synapse_repository(db_session):
    repo = QuantumDotsOptoelectronicSynapseRepository(db_session)

    study = await repo.create_study(
        name="Study_453_Verification",
        target_specimen="InP/ZnS Core-Shell Quantum Dot Photo-Memristor Synapse Coupled to Primary Cortical Neurons",
        analytical_modality="qd-optoelectronic-synapse",
        paired_pulse_facilitation_ppf_ratio=1.82,
        photocurrent_relaxation_lifetime_ms=245.0,
        synaptic_weight_plasticity_dynamic_range=4.65,
        energy_consumption_per_spike_femtojoules=82.0,
        confidence_score=0.991,
        status="completed",
        summary_report="Phase 453 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_453_Verification"
    assert study.paired_pulse_facilitation_ppf_ratio == 1.82

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Optoelectronic_Excitatory_Postsynaptic_Current",
        profile_category="Primary Step",
        quantitative_value=1.82,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Optoelectronic_Excitatory_Postsynaptic_Current"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="paired_pulse_facilitation_ppf_ratio",
        observed_value=1.82,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 1.82

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_453_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
