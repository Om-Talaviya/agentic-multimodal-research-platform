"""Tests for Phase 339: Autonomous CAR-T TCR-pMHC Cross-Reactivity & Structural Off-Target Immunotoxicity Assayer Engine."""

import pytest
from research.orchestration.car_tcr_cross_reactivity_assayer_engine import CarTcrCrossReactivityAssayerEngine


def test_car_tcr_cross_reactivity_assayer_engine():
    engine = CarTcrCrossReactivityAssayerEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="car-tcr-cross-reactivity",
        input_scale=1.0,
    )
    assert getattr(result, "self_epitope_cross_reactivity_safety_index") != 0
    assert getattr(result, "off_target_binding_free_energy_delta_g_score") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
