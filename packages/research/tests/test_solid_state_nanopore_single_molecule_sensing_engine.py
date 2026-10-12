"""Tests for Phase 417: Autonomous Solid-State Silicon Nitride Nanopore Single-Molecule Protein Translocation Engine."""

import pytest
from research.orchestration.solid_state_nanopore_single_molecule_sensing_engine import SolidStateNanoporeSensingEngine


def test_solid_state_nanopore_single_molecule_sensing_engine():
    engine = SolidStateNanoporeSensingEngine()
    result = engine.analyze(
        target_specimen="Conformationally Stretched Native Protein Translocation Through Sub-5nm SiNx Nanopore",
        analytical_modality="solid-state-nanopore",
        input_scale=1.0,
    )

    assert result.target_specimen == "Conformationally Stretched Native Protein Translocation Through Sub-5nm SiNx Nanopore"
    assert result.confidence_score >= 0.95
    assert result.translocation_dwell_time_us > 0.0
    assert result.fractional_current_blockade_ratio > 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Solid-State Silicon" in result.summary_report
