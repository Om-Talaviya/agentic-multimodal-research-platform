"""Tests for Phase 190: Thermal Proteome Profiling & Target Engagement Deconvolution Engine Engine."""

import pytest
from research.proteomics.thermal_proteome_profiling_engine import ThermalProteomeProfilingEngine


def test_thermal_proteome_profiling_engine():
    engine = ThermalProteomeProfilingEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="Thermal Proteome Profiling TPP",
        input_scale=1.0,
    )
    assert getattr(result, "melting_temperature_shift_celsius") > 0
    assert getattr(result, "target_engagement_confidence_auc") > 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
