"""Tests for Phase 383: Autonomous In Vivo Viral Vector Tropism De-Targeting & Liver-Sparing Engineered Capsid Selector Engine."""

import pytest
from research.orchestration.viral_tropism_detargeting_engine import ViralTropismDetargetingEngine


def test_viral_tropism_detargeting_engine():
    engine = ViralTropismDetargetingEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="viral-tropism-detargeting",
        input_scale=1.0,
    )
    assert getattr(result, "hepatic_sequestration_reduction_ratio_fold") != 0
    assert getattr(result, "target_tissue_cns_transduction_enrichment_fold") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
