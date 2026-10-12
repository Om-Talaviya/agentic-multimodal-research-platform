"""Tests for Phase 427: Autonomous CRISPR C-to-G Base Editor (CGBE) & Cas12f Miniature Transposon Editing Forecaster."""

import pytest
from research.orchestration.cgbe_cas12f_miniature_editing_engine import CgbeCas12fMiniatureEditingEngine


def test_cgbe_cas12f_miniature_editing_engine():
    engine = CgbeCas12fMiniatureEditingEngine()
    result = engine.analyze(
        target_specimen="Ultra-Compact Cas12f Miniature CGBE Complex in AAV Vector",
        analytical_modality="cgbe-cas12f-editing",
        input_scale=1.0,
    )

    assert result.target_specimen == "Ultra-Compact Cas12f Miniature CGBE Complex in AAV Vector"
    assert result.confidence_score >= 0.95
    assert result.c_to_g_conversion_purity_percent > 0.0
    assert result.on_target_indel_frequency_percent > 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous CRISPR C-to-G Base " in result.summary_report
