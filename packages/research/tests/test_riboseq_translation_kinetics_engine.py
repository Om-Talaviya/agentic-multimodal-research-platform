"""Tests for Phase 196: Ribosome Profiling & Translation Efficiency Deconvolution Engine Engine."""

import pytest
from research.genomics.riboseq_translation_kinetics_engine import RiboSeqTranslationKineticsEngine


def test_riboseq_translation_kinetics_engine():
    engine = RiboSeqTranslationKineticsEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="Ribo-seq Translation Kinetics",
        input_scale=1.0,
    )
    assert getattr(result, "mean_translation_efficiency_log2") > 0
    assert getattr(result, "ribosome_dwell_time_ms") > 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
