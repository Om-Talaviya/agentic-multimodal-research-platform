"""Tests for Phase 404: Deep Multi-Task CRISPR Prime Editing RT-Template Efficiency Forecaster Engine."""

import pytest
from research.orchestration.crispr_prime_editing_efficiency_engine import CrisprPrimeEditingEfficiencyEngine


def test_crispr_prime_editing_efficiency_engine():
    engine = CrisprPrimeEditingEfficiencyEngine()
    result = engine.analyze(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="crispr-prime-editing-efficiency",
        input_scale=1.0,
    )

    assert result.target_specimen == "Human Patient Cohort Sample"
    assert result.confidence_score >= 0.95
    assert getattr(result, "prime_editing_intended_insertion_efficiency_pct") > 0
    assert getattr(result, "indel_byproduct_purity_ratio_intended_to_indel") > 0
    assert len(result.item_profiles) == 3
    assert len(result.metric_traces) == 3
    assert "Phase 404" in result.summary_report
