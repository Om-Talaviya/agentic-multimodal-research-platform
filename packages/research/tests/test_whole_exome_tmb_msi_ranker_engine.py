"""Tests for Phase 218: Autonomous Whole-Exome Sequencing (WES) Tumor Mutation Burden (TMB) & Microsatellite Instability (MSI) Ranker Engine Engine."""

import pytest
from research.orchestration.whole_exome_tmb_msi_ranker_engine import WholeExomeTmbMsiRankerEngine


def test_whole_exome_tmb_msi_ranker_engine():
    engine = WholeExomeTmbMsiRankerEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="whole-exome-tmb-msi-ranker",
        input_scale=1.0,
    )
    assert getattr(result, "tmb_mutations_per_mb") != 0
    assert getattr(result, "msi_instability_score_pct") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
