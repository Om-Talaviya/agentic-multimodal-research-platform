"""Tests for Phase 423: Autonomous Synthetic Minimal Cell Membrane Lipid Bilayer Asymmetry & Vesicle Budding Engine."""

import pytest
from research.orchestration.minimal_cell_lipid_asymmetry_engine import MinimalCellLipidAsymmetryEngine


def test_minimal_cell_lipid_asymmetry_engine():
    engine = MinimalCellLipidAsymmetryEngine()
    result = engine.analyze(
        target_specimen="Synthetic Giant Unilamellar Vesicle (GUV) with Flippase ABCB4",
        analytical_modality="minimal-cell-lipid",
        input_scale=1.0,
    )

    assert result.target_specimen == "Synthetic Giant Unilamellar Vesicle (GUV) with Flippase ABCB4"
    assert result.confidence_score >= 0.95
    assert result.bilayer_asymmetry_index > 0.0
    assert result.membrane_bending_rigidity_kbt > 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Synthetic Minimal C" in result.summary_report
