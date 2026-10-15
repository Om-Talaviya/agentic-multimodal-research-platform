"""Tests for Phase 531: Autonomous Spatially-Resolved Optogenetic Mitochondrial Calcium Spark & Bioenergetics Modeler."""

import pytest
from research.orchestration.optogenetic_mitochondrial_calcium_oscillator_engine import OptogeneticMitochondrialCalciumOscillatorEngine


def test_optogenetic_mitochondrial_calcium_oscillator_engine():
    engine = OptogeneticMitochondrialCalciumOscillatorEngine()
    result = engine.analyze(
        target_specimen="Human Cardiomyocyte Syncytium with Mitochondrially-Targeted ChR2 and R-GECO1 Probes",
        analytical_modality="optogenetic-mitochondrial-calcium",
        input_scale=1.0,
    )

    assert result.target_specimen == "Human Cardiomyocyte Syncytium with Mitochondrially-Targeted ChR2 and R-GECO1 Probes"
    assert result.confidence_score >= 0.95
    assert result.matrix_calcium_influx_rate_uM_per_s != 0.0
    assert result.mcu_channel_open_probability != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Spatially-Resolved " in result.summary_report
