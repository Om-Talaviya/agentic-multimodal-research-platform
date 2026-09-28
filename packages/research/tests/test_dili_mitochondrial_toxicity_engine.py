"""Tests for Phase 250: Autonomous Multi-Omics Drug-Induced Liver Injury (DILI) & Mitochondrial Toxicity Forecaster Engine Engine."""

import pytest
from research.orchestration.dili_mitochondrial_toxicity_engine import DiliMitochondrialToxicityEngine


def test_dili_mitochondrial_toxicity_engine():
    engine = DiliMitochondrialToxicityEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="dili-mitochondrial-toxicity",
        input_scale=1.0,
    )
    assert getattr(result, "dili_clinical_severity_prediction_auc") != 0
    assert getattr(result, "mitochondrial_dissipation_ic50_uM") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
