"""Tests for Phase 457: Autonomous Biohybrid Cybernetic Soft Actuator Myotube Electromechanical Force Forecaster."""

import pytest
from research.orchestration.biohybrid_soft_actuator_myotube_engine import BiohybridSoftActuatorMyotubeEngine


def test_biohybrid_soft_actuator_myotube_engine():
    engine = BiohybridSoftActuatorMyotubeEngine()
    result = engine.analyze(
        target_specimen="3D Bioprinted Optogenetic C2C12 Skeletal Myotube Cantilever on Flexible Hydrogel Skeleton",
        analytical_modality="biohybrid-actuator-mechanics",
        input_scale=1.0,
    )

    assert result.target_specimen == "3D Bioprinted Optogenetic C2C12 Skeletal Myotube Cantilever on Flexible Hydrogel Skeleton"
    assert result.confidence_score >= 0.95
    assert result.active_contractile_force_micro_newtons != 0.0
    assert result.twitch_to_tetanus_force_ratio != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Biohybrid Cyberneti" in result.summary_report
