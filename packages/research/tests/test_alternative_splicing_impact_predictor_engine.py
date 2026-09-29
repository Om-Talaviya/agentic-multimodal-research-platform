"""Tests for Phase 343: Autonomous Whole-Transcriptome Alternative Splicing & Exon Skipping Functional Impact Predictor Engine."""

import pytest
from research.orchestration.alternative_splicing_impact_predictor_engine import AlternativeSplicingImpactPredictorEngine


def test_alternative_splicing_impact_predictor_engine():
    engine = AlternativeSplicingImpactPredictorEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="alternative-splicing-impact",
        input_scale=1.0,
    )
    assert getattr(result, "percent_spliced_in_psi_shift_delta_pct") != 0
    assert getattr(result, "nonsense_mediated_decay_evasion_probability_pct") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
