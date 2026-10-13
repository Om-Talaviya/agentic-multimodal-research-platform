"""Tests for Phase 444: Autonomous Optogenetic Membrane Depolarization & Action Potential Firing Trajectory Simulator."""

import pytest
from research.orchestration.optogenetic_action_potential_trajectory_engine import OptogeneticActionPotentialEngine


def test_optogenetic_action_potential_trajectory_engine():
    engine = OptogeneticActionPotentialEngine()
    result = engine.analyze(
        target_specimen="Channelrhodopsin-2 (ChR2) Expressing Cortical Pyramidal Neurons under 470nm Pulsed Blue Light",
        analytical_modality="optogenetic-membrane-depolarization",
        input_scale=1.0,
    )

    assert result.target_specimen == "Channelrhodopsin-2 (ChR2) Expressing Cortical Pyramidal Neurons under 470nm Pulsed Blue Light"
    assert result.confidence_score >= 0.95
    assert result.membrane_depolarization_rate_mv_per_ms > 0.0
    assert result.action_potential_firing_fidelity > 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Optogenetic Membran" in result.summary_report
