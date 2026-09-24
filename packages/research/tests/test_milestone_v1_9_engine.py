"""Tests for MilestoneV19SynthesisEngine (Phase 161)."""

from research.orchestration.milestone_v1_9_engine import (
    MilestoneV19SynthesisEngine,
    MilestoneV19StratificationRequest,
)


def test_milestone_v1_9_engine():
    engine = MilestoneV19SynthesisEngine()
    req = MilestoneV19StratificationRequest(
        cohort_study_name="Pan-Cancer Precision Stratification Test",
        patient_cohort_size=10000,
        active_phases_count=161,
    )
    result = engine.stratify_cohort(req)
    assert result.total_phases_integrated == 161
    assert result.clusters_identified_count == 4
    assert len(result.clusters) == 4
    assert len(result.efficacy_matrix) == 4
