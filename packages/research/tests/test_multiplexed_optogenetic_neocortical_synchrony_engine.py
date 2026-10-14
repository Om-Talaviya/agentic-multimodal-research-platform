"""Tests for Phase 517: Autonomous Dual-Color Multiplexed Optogenetic Neocortical Oscillatory Synchrony Mapper."""

import pytest
from research.orchestration.multiplexed_optogenetic_neocortical_synchrony_engine import MultiplexedOptogeneticNeocorticalSynchronyEngine


def test_multiplexed_optogenetic_neocortical_synchrony_engine():
    engine = MultiplexedOptogeneticNeocorticalSynchronyEngine()
    result = engine.analyze(
        target_specimen="Transgenic Mouse Somatosensory Cortex expressing ChRmine (Red) and ChETA (Blue) in Layer 2/3 and 5",
        analytical_modality="dual-color-optogenetic-synchrony",
        input_scale=1.0,
    )

    assert result.target_specimen == "Transgenic Mouse Somatosensory Cortex expressing ChRmine (Red) and ChETA (Blue) in Layer 2/3 and 5"
    assert result.confidence_score >= 0.95
    assert result.gamma_band_phase_locking_value_plv != 0.0
    assert result.optical_crosstalk_attenuation_ratio != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Dual-Color Multiple" in result.summary_report
