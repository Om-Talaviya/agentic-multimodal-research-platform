"""Tests for Phase 262: Autonomous High-Throughput Perturb-seq Deep Causal Gene Regulatory Network Inversion & Epistasis Engine Engine."""

import pytest
from research.orchestration.perturb_seq_epistasis_causal_network_engine import PerturbSeqEpistasisCausalNetworkEngine


def test_perturb_seq_epistasis_causal_network_engine():
    engine = PerturbSeqEpistasisCausalNetworkEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="perturb-seq-epistasis-causal-network",
        input_scale=1.0,
    )
    assert getattr(result, "causal_edge_reconstruction_precision_pct") != 0
    assert getattr(result, "epistasis_synergy_detection_power") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
