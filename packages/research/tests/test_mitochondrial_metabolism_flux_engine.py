"""Tests for Phase 411: Single-Cell Mitochondrial Bioenergetics & OCR/ECAR Metabolic Flux Balance Simulator Engine."""

import pytest
from research.orchestration.mitochondrial_metabolism_flux_engine import MitochondrialMetabolismFluxEngine


def test_mitochondrial_metabolism_flux_engine():
    engine = MitochondrialMetabolismFluxEngine()
    result = engine.analyze(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="mitochondrial-metabolism-flux",
        input_scale=1.0,
    )

    assert result.target_specimen == "Human Patient Cohort Sample"
    assert result.confidence_score >= 0.95
    assert getattr(result, "oxygen_consumption_rate_ocr_pmol_per_min") > 0
    assert getattr(result, "mitochondrial_spare_respiratory_capacity_ratio") > 0
    assert len(result.item_profiles) == 3
    assert len(result.metric_traces) == 3
    assert "Phase 411" in result.summary_report
