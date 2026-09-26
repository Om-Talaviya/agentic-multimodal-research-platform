"""Tests for Phase 200: Epigenomic Hi-ChIP & Enhancer-Promoter Chromatin Looping Engine Engine."""

import pytest
from research.genomics.hichip_chromatin_looping_engine import HiChIPChromatinLoopingEngine


def test_hichip_chromatin_looping_engine():
    engine = HiChIPChromatinLoopingEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="Hi-ChIP Chromatin Looping",
        input_scale=1.0,
    )
    assert getattr(result, "loop_contact_enrichment_score") > 0
    assert getattr(result, "enhancer_promoter_interaction_strength") > 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
