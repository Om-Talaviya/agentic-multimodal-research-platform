"""Tests for Phase 302: Autonomous In-Silico Whole-Organ Vascular Micro-Perfusion & Dynamic Oxygen Gradient Hemodynamics Simulator Engine."""

import pytest
from research.orchestration.whole_organ_vascular_perfusion_engine import WholeOrganVascularPerfusionEngine


def test_whole_organ_vascular_perfusion_engine():
    engine = WholeOrganVascularPerfusionEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="whole-organ-vascular-perfusion",
        input_scale=1.0,
    )
    assert getattr(result, "microvascular_perfusion_flow_rate_mL_min") != 0
    assert getattr(result, "tissue_hypoxia_gradient_dissipation_r2") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
