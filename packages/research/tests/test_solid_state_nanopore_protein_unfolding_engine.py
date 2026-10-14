"""Tests for Phase 508: Autonomous Solid-State Nanopore Single-Molecule Protein Co-Translocational Unfolding Modeler."""

import pytest
from research.orchestration.solid_state_nanopore_protein_unfolding_engine import SolidStateNanoporeProteinUnfoldingEngine


def test_solid_state_nanopore_protein_unfolding_engine():
    engine = SolidStateNanoporeProteinUnfoldingEngine()
    result = engine.analyze(
        target_specimen="Sub-3nm Low-Noise HfO2 Nanopore with ClpX-Coupled Maltose-Binding Protein Translocation",
        analytical_modality="nanopore-protein-unfolding",
        input_scale=1.0,
    )

    assert result.target_specimen == "Sub-3nm Low-Noise HfO2 Nanopore with ClpX-Coupled Maltose-Binding Protein Translocation"
    assert result.confidence_score >= 0.95
    assert result.unfolding_energy_barrier_height_kbT != 0.0
    assert result.translocation_dwell_time_per_domain_ms != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Solid-State Nanopor" in result.summary_report
