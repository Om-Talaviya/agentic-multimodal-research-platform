"""Tests for Phase 494: Autonomous Mechanosensitive Ion Channel PIEZO1 Gating & Membrane Tension Indentation Engine."""

import pytest
from research.orchestration.piezo_mechanosensitive_channel_gating_engine import PiezoMechanosensitiveChannelGatingEngine


def test_piezo_mechanosensitive_channel_gating_engine():
    engine = PiezoMechanosensitiveChannelGatingEngine()
    result = engine.analyze(
        target_specimen="High-Speed Pressure Clamped HEK293 Cell expressing Human PIEZO1 Trimeric Propeller Blades",
        analytical_modality="piezo-mechanosensitive-gating",
        input_scale=1.0,
    )

    assert result.target_specimen == "High-Speed Pressure Clamped HEK293 Cell expressing Human PIEZO1 Trimeric Propeller Blades"
    assert result.confidence_score >= 0.95
    assert result.half_maximal_activation_tension_mN_per_m != 0.0
    assert result.channel_open_probability_p_open != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Mechanosensitive Io" in result.summary_report
