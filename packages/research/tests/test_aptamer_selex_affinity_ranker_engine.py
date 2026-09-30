"""Tests for Phase 394: In-Silico Systematic Evolution of Ligands (SELEX) Aptamer Affinity Ranker Engine."""

import pytest
from research.orchestration.aptamer_selex_affinity_ranker_engine import AptamerSelexAffinityRankerEngine


def test_aptamer_selex_affinity_ranker_engine():
    engine = AptamerSelexAffinityRankerEngine()
    result = engine.analyze(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="aptamer-selex-affinity-ranking",
        input_scale=1.0,
    )

    assert result.target_specimen == "Human Patient Cohort Sample"
    assert result.confidence_score >= 0.95
    assert getattr(result, "aptamer_target_dissociation_constant_kd_nm") > 0
    assert getattr(result, "counter_selex_off_target_discrimination_ratio") > 0
    assert len(result.item_profiles) == 3
    assert len(result.metric_traces) == 3
    assert "Phase 394" in result.summary_report
