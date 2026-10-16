"""Tests for Phase 556: Autonomous Synthetic Mammalian Gene Circuit Feedback Integral Controller for Homeostatic Glucose Regulation."""

import pytest
from research.orchestration.mammalian_gene_circuit_homeostatic_controller_engine import MammalianGeneCircuitHomeostaticControllerEngine


def test_mammalian_gene_circuit_homeostatic_controller_engine():
    engine = MammalianGeneCircuitHomeostaticControllerEngine()
    result = engine.analyze(
        target_specimen="Engineered Beta-Cell Like HEK-293T cells expressing Synthetic Glucose-Sensing Integral Antithetic Feedback Invertible Controller",
        analytical_modality="synthetic-homeostatic-circuit",
        input_scale=1.0,
    )

    assert result.target_specimen == "Engineered Beta-Cell Like HEK-293T cells expressing Synthetic Glucose-Sensing Integral Antithetic Feedback Invertible Controller"
    assert result.confidence_score >= 0.95
    assert result.homeostatic_glucose_setpoint_steady_state_mg_dl != 0.0
    assert result.integral_control_settling_time_minutes != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Synthetic Mammalian" in result.summary_report
