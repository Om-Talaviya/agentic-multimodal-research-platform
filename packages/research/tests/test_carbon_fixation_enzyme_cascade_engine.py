"""Tests for Phase 374: Autonomous Synthetic Carbon-Fixation Multi-Enzyme Cascade Flux Balancer Engine."""

import pytest
from research.orchestration.carbon_fixation_enzyme_cascade_engine import CarbonFixationEnzymeCascadeEngine


def test_carbon_fixation_enzyme_cascade_engine():
    engine = CarbonFixationEnzymeCascadeEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="carbon-fixation-enzyme-cascade",
        input_scale=1.0,
    )
    assert getattr(result, "catalytic_co2_assimilation_rate_umol_min_mg") != 0
    assert getattr(result, "nadph_electron_conversion_efficiency_pct") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
