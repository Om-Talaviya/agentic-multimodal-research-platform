"""Tests for Phase 361: Autonomous Target-Activated Pro-Drug (ADC/PDC) Cleavable Linker Hydrolysis & Payload Release Simulator Engine."""

import pytest
from research.orchestration.adc_linker_cleavage_simulator_engine import AdcLinkerCleavageSimulatorEngine


def test_adc_linker_cleavage_simulator_engine():
    engine = AdcLinkerCleavageSimulatorEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="adc-linker-cleavage-simulator",
        input_scale=1.0,
    )
    assert getattr(result, "intracellular_payload_release_efficiency_pct") != 0
    assert getattr(result, "plasma_circulation_premature_leakage_rate_pct_day") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
