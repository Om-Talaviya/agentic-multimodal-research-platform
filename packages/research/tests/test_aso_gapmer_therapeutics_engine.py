"""Tests for Phase 193: Antisense Oligonucleotide RNase-H Cleavage & Gapmer Engine Engine."""

import pytest
from research.therapeutics.aso_gapmer_therapeutics_engine import ASOGapmerTherapeuticsEngine


def test_aso_gapmer_therapeutics_engine():
    engine = ASOGapmerTherapeuticsEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="Antisense Oligonucleotide Gapmer",
        input_scale=1.0,
    )
    assert getattr(result, "rnase_h_cleavage_velocity_min") > 0
    assert getattr(result, "target_knockdown_percent") > 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
