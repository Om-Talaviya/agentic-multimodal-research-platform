"""Tests for Phase 348: Autonomous High-Throughput Surface Plasmon Resonance (HT-SPR) Kinetic Binding Rate Constants Extractor Engine."""

import pytest
from research.orchestration.ht_spr_kinetic_rate_extractor_engine import HtSprKineticRateExtractorEngine


def test_ht_spr_kinetic_rate_extractor_engine():
    engine = HtSprKineticRateExtractorEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="ht-spr-kinetics",
        input_scale=1.0,
    )
    assert getattr(result, "kinetic_dissociation_constant_kd_picomolar") != 0
    assert getattr(result, "spr_sensorgram_global_fit_confidence_pct") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
