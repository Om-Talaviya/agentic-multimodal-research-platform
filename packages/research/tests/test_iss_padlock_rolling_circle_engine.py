"""Tests for Phase 289: Autonomous Spatial Multi-Omics Whole-Transcriptome In-Situ Sequencing (ISS) Padlock Decoding Engine Engine."""

import pytest
from research.orchestration.iss_padlock_rolling_circle_engine import IssPadlockRollingCircleEngine


def test_iss_padlock_rolling_circle_engine():
    engine = IssPadlockRollingCircleEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="iss-padlock-rolling-circle",
        input_scale=1.0,
    )
    assert getattr(result, "optical_decoding_accuracy_pct") != 0
    assert getattr(result, "subcellular_rca_puncta_density_per_100um2") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
