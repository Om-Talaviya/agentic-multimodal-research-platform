"""Tests for Phase 450: Autonomous Nanopore Ionic Current Blockade Shape Classifier for Macromolecular Topologies."""

import pytest
from research.orchestration.nanopore_blockade_topology_classifier_engine import NanoporeBlockadeTopologyEngine


def test_nanopore_blockade_topology_classifier_engine():
    engine = NanoporeBlockadeTopologyEngine()
    result = engine.analyze(
        target_specimen="Supercoiled Plasmid DNA and Knotted Circular Peptides Passing Through 4nm Aerolysin Pore",
        analytical_modality="nanopore-blockade-topology",
        input_scale=1.0,
    )

    assert result.target_specimen == "Supercoiled Plasmid DNA and Knotted Circular Peptides Passing Through 4nm Aerolysin Pore"
    assert result.confidence_score >= 0.95
    assert result.dwell_time_topological_knot_us != 0.0
    assert result.fractional_blockade_current_depth_ratio != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Nanopore Ionic Curr" in result.summary_report
