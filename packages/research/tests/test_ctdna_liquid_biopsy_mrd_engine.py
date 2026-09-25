"""Tests for Phase 194: Pan-Cancer ctDNA Liquid Biopsy & Minimal Residual Disease Engine Engine."""

import pytest
from research.diagnostics.ctdna_liquid_biopsy_mrd_engine import CtDNALiquidBiopsyMRDEngine


def test_ctdna_liquid_biopsy_mrd_engine():
    engine = CtDNALiquidBiopsyMRDEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="ctDNA Liquid Biopsy MRD",
        input_scale=1.0,
    )
    assert getattr(result, "mean_tumor_fraction_clearance_percent") > 0
    assert getattr(result, "mrd_recurrence_hazard_ratio") > 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
