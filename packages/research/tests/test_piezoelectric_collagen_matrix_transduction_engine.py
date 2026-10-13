"""Tests for Phase 470: Autonomous Bio-Piezoelectric Collagen Matrix Electromechanical Transduction Engine."""

import pytest
from research.orchestration.piezoelectric_collagen_matrix_transduction_engine import PiezoelectricCollagenMatrixTransductionEngine


def test_piezoelectric_collagen_matrix_transduction_engine():
    engine = PiezoelectricCollagenMatrixTransductionEngine()
    result = engine.analyze(
        target_specimen="Dense Fibrillar Type-I Collagen Fascicle Scaffold with Applied High-Frequency Axial Dynamic Strain",
        analytical_modality="piezoelectric-collagen-transduction",
        input_scale=1.0,
    )

    assert result.target_specimen == "Dense Fibrillar Type-I Collagen Fascicle Scaffold with Applied High-Frequency Axial Dynamic Strain"
    assert result.confidence_score >= 0.95
    assert result.piezoelectric_coefficient_d33_pC_per_N != 0.0
    assert result.surface_potential_streaming_voltage_mV != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Bio-Piezoelectric C" in result.summary_report
