"""Tests for Phase 570: Autonomous Synthetic DNA Strand Displacement (DSD) Molecular Neural Network Winner-Take-All Classifier Engine."""

import pytest
from research.orchestration.synthetic_dna_strand_displacement_neural_gate_engine import SyntheticDnaStrandDisplacementNeuralGateEngine


def test_synthetic_dna_strand_displacement_neural_gate_engine():
    engine = SyntheticDnaStrandDisplacementNeuralGateEngine()
    result = engine.analyze(
        target_specimen="Toehold-Mediated 4-Input 2-Class DNA Strand Displacement Reaction Network in Tris-Acetate-EDTA Buffer",
        analytical_modality="dsd-molecular-neural-classification",
        input_scale=1.0,
    )
    assert result is not None
    assert result.toehold_exchange_rate_constant_m_s != 0.0
    assert result.signal_to_leakage_ratio != 0.0
    assert result.winner_take_all_convergence_time_s != 0.0
    assert result.decision_boundary_sharpness != 0.0
    assert result.confidence_score >= 0.90
    assert len(result.item_profiles) == 3
    assert len(result.metric_traces) == 3
    assert result.target_specimen == "Toehold-Mediated 4-Input 2-Class DNA Strand Displacement Reaction Network in Tris-Acetate-EDTA Buffer"
    assert result.analytical_modality == "dsd-molecular-neural-classification"
