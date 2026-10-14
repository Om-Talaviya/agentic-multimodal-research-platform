"""Tests for Phase 521: Autonomous Biomolecular Protein Nanofiber Memristive Synaptic Weight Plasticity Forecaster."""

import pytest
from research.orchestration.neuromorphic_memristive_synapse_protein_engine import NeuromorphicMemristiveSynapseProteinEngine


def test_neuromorphic_memristive_synapse_protein_engine():
    engine = NeuromorphicMemristiveSynapseProteinEngine()
    result = engine.analyze(
        target_specimen="Crossbar Array of Self-Assembled Amyloid-beta / Ferritin Bio-Nanowires sandwiched between Pt/Au Electrodes",
        analytical_modality="biomolecular-memristor-plasticity",
        input_scale=1.0,
    )

    assert result.target_specimen == "Crossbar Array of Self-Assembled Amyloid-beta / Ferritin Bio-Nanowires sandwiched between Pt/Au Electrodes"
    assert result.confidence_score >= 0.95
    assert result.conductance_switching_on_off_ratio != 0.0
    assert result.spike_timing_dependent_plasticity_stdp_tau_ms != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Biomolecular Protei" in result.summary_report
