"""Tests for Phase 400: Autonomous Whole-Exome Tumor Mutational Burden & Microsatellite Instability Evaluator Engine."""

import pytest
from research.orchestration.whole_exome_tmb_msi_evaluator_engine import WholeExomeTmbMsiEvaluatorEngine


def test_whole_exome_tmb_msi_evaluator_engine():
    engine = WholeExomeTmbMsiEvaluatorEngine()
    result = engine.analyze(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="whole-exome-tmb-msi-evaluation",
        input_scale=1.0,
    )

    assert result.target_specimen == "Human Patient Cohort Sample"
    assert result.confidence_score >= 0.95
    assert getattr(result, "tumor_mutational_burden_mut_per_megabase") > 0
    assert getattr(result, "msi_high_classification_confidence_pct") > 0
    assert len(result.item_profiles) == 3
    assert len(result.metric_traces) == 3
    assert "Phase 400" in result.summary_report
