"""Tests for MilestoneV18SynthesisEngine (Phase 154)."""

from research.orchestration.milestone_v1_8_engine import (
    MilestoneV18SynthesisEngine,
    MilestoneV18SynthesisRequest,
)


def test_milestone_v1_8_engine():
    engine = MilestoneV18SynthesisEngine()
    req = MilestoneV18SynthesisRequest(
        orchestration_name="Milestone v1.8 Centennial Integration",
        target_indication="GBM & Immuno-Oncology",
        active_phases_count=154,
    )
    result = engine.synthesize(req)
    assert result.total_phases_integrated == 154
    assert result.orchestration_confidence_score > 0.95
    assert len(result.workflow_nodes) == 8
    assert len(result.executive_reports) == 1
