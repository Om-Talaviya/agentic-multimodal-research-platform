"""Tests for Phase 424: Autonomous Deep Mutational Scanning (DMS) Variant Fitness & Thermostability Epistasis Forecaster."""

import pytest
from research.orchestration.deep_mutational_scanning_epistasis_engine import DeepMutationalScanningEpistasisEngine


def test_deep_mutational_scanning_epistasis_engine():
    engine = DeepMutationalScanningEpistasisEngine()
    result = engine.analyze(
        target_specimen="Beta-Lactamase All-Combinatorial Single/Double Point Mutants",
        analytical_modality="dms-epistasis",
        input_scale=1.0,
    )

    assert result.target_specimen == "Beta-Lactamase All-Combinatorial Single/Double Point Mutants"
    assert result.confidence_score >= 0.95
    assert result.higher_order_epistasis_coefficient > 0.0
    assert result.relative_fitness_enrichment_ratio > 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Deep Mutational Sca" in result.summary_report
