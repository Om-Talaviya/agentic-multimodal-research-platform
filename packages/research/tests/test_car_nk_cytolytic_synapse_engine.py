"""Tests for Phase 198: CAR-NK Immune Synapse & Cytolytic Kinetics Simulator Engine."""

import pytest
from research.immunology.car_nk_cytolytic_synapse_engine import CARNKCytolyticSynapseEngine


def test_car_nk_cytolytic_synapse_engine():
    engine = CARNKCytolyticSynapseEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="CAR-NK Cytolytic Synapse",
        input_scale=1.0,
    )
    assert getattr(result, "cytolytic_specific_lysis_percent") > 0
    assert getattr(result, "synapse_polarization_time_minutes") > 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
