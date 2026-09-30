"""Tests for Phase 377: Autonomous High-Throughput Optical Pooled CRISPR Screening Phenotypic Image Decoder Engine."""

import pytest
from research.orchestration.optical_pooled_crispr_screening_engine import OpticalPooledCrisprScreeningEngine


def test_optical_pooled_crispr_screening_engine():
    engine = OpticalPooledCrisprScreeningEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="optical-pooled-crispr-screening",
        input_scale=1.0,
    )
    assert getattr(result, "optical_barcode_calling_accuracy_pct") != 0
    assert getattr(result, "single_cell_phenotype_classification_f1_score") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
