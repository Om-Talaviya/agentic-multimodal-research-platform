"""Tests for Phase 410: High-Density MEA Real-Time Neuromorphic Action Potential Spike Sorter Engine."""

import pytest
from research.orchestration.high_density_mea_spike_sorting_engine import HighDensityMeaSpikeSortingEngine


def test_high_density_mea_spike_sorting_engine():
    engine = HighDensityMeaSpikeSortingEngine()
    result = engine.analyze(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="high-density-mea-spike-sorting",
        input_scale=1.0,
    )

    assert result.target_specimen == "Human Patient Cohort Sample"
    assert result.confidence_score >= 0.95
    assert getattr(result, "spike_sorting_single_unit_isolation_f1_score") > 0
    assert getattr(result, "realtime_neuromorphic_processing_latency_us") > 0
    assert len(result.item_profiles) == 3
    assert len(result.metric_traces) == 3
    assert "Phase 410" in result.summary_report
