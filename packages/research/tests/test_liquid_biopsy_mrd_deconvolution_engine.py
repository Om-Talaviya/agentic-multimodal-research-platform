"""Tests for Phase 264: Autonomous Multi-Omics Microscopic Residual Disease (MRD) & Ultra-Low VAF Liquid Biopsy Deconvolution Engine Engine."""

import pytest
from research.orchestration.liquid_biopsy_mrd_deconvolution_engine import LiquidBiopsyMrdDeconvolutionEngine


def test_liquid_biopsy_mrd_deconvolution_engine():
    engine = LiquidBiopsyMrdDeconvolutionEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="liquid-biopsy-mrd-deconvolution",
        input_scale=1.0,
    )
    assert getattr(result, "mrd_limit_of_detection_vaf_pct") != 0
    assert getattr(result, "chip_variant_filtration_specificity_pct") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
