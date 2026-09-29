"""Tests for Phase 353: Autonomous Whole-Brain 2-Photon Calcium Imaging Neural Circuit Dynamics & Attractor Network Modeler Engine."""

import pytest
from research.orchestration.two_photon_neural_dynamics_engine import TwoPhotonNeuralDynamicsEngine


def test_two_photon_neural_dynamics_engine():
    engine = TwoPhotonNeuralDynamicsEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="two-photon-neural-dynamics",
        input_scale=1.0,
    )
    assert getattr(result, "spike_inference_temporal_precision_ms") != 0
    assert getattr(result, "neural_population_attractor_coherence_pct") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
