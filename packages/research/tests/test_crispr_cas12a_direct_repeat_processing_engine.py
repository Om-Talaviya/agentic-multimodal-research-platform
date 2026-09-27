"""Tests for Phase 227: Autonomous CRISPR-Cas12a Multiplex crRNA Array Self-Processing & Asymmetric Cleavage Engine Engine."""

import pytest
from research.orchestration.crispr_cas12a_direct_repeat_processing_engine import CrisprCas12aDirectRepeatProcessingEngine


def test_crispr_cas12a_direct_repeat_processing_engine():
    engine = CrisprCas12aDirectRepeatProcessingEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="crispr-cas12a-direct-repeat-processing",
        input_scale=1.0,
    )
    assert getattr(result, "crrna_processing_efficiency_pct") != 0
    assert getattr(result, "collateral_ssdna_trans_cleavage_rate") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
