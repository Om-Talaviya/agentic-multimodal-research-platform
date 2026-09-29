"""Tests for Phase 340: Autonomous CRISPR Non-Homologous End Joining (NHEJ) vs HDR Repair Outcome Probability Forecaster Engine."""

import pytest
from research.orchestration.crispr_repair_outcome_forecaster_engine import CrisprRepairOutcomeForecasterEngine


def test_crispr_repair_outcome_forecaster_engine():
    engine = CrisprRepairOutcomeForecasterEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="crispr-repair-forecaster",
        input_scale=1.0,
    )
    assert getattr(result, "predicted_repair_profile_accuracy_pct") != 0
    assert getattr(result, "precision_in_frame_editing_frequency_pct") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
