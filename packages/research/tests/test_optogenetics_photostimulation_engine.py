"""Tests for Phase 210: Autonomous Optogenetic Photostimulation Pattern Synthesis & Neuronal Spike Raster Forecaster Engine Engine."""

import pytest
from research.orchestration.optogenetics_photostimulation_engine import OptogeneticsPhotostimulationEngine


def test_optogenetics_photostimulation_engine():
    engine = OptogeneticsPhotostimulationEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="optogenetics-photostimulation",
        input_scale=1.0,
    )
    assert getattr(result, "spike_fidelity_pct") != 0
    assert getattr(result, "photocurrent_density_pA_um2") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
