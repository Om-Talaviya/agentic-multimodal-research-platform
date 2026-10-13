"""Tests for Phase 463: Autonomous Neural Organoid Spontaneous Synchronous Bursting & Functional Connectivity Grapher."""

import pytest
from research.orchestration.neural_organoid_bursting_connectivity_engine import NeuralOrganoidBurstingConnectivityEngine


def test_neural_organoid_bursting_connectivity_engine():
    engine = NeuralOrganoidBurstingConnectivityEngine()
    result = engine.analyze(
        target_specimen="6-Month Human Cerebral Cortical Organoid on 4096-Channel CMOS High-Density MEA",
        analytical_modality="organoid-neural-connectivity",
        input_scale=1.0,
    )

    assert result.target_specimen == "6-Month Human Cerebral Cortical Organoid on 4096-Channel CMOS High-Density MEA"
    assert result.confidence_score >= 0.95
    assert result.synchronous_network_burst_rate_hz != 0.0
    assert result.graph_small_world_clustering_coefficient != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Neural Organoid Spo" in result.summary_report
