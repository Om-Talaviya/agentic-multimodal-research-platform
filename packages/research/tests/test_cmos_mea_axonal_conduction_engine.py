"""Tests for Phase 490: Autonomous High-Density CMOS Microelectrode Array Neuromorphic Axonal Conduction Velocity Mapper."""

import pytest
from research.orchestration.cmos_mea_axonal_conduction_engine import CmosMeaAxonalConductionEngine


def test_cmos_mea_axonal_conduction_engine():
    engine = CmosMeaAxonalConductionEngine()
    result = engine.analyze(
        target_specimen="Rat Cortical Primary Neurons Cultured over 26,400 Platinum Electrode CMOS Biocompatible Chip",
        analytical_modality="cmos-mea-axonal-conduction",
        input_scale=1.0,
    )

    assert result.target_specimen == "Rat Cortical Primary Neurons Cultured over 26,400 Platinum Electrode CMOS Biocompatible Chip"
    assert result.confidence_score >= 0.95
    assert result.axonal_action_potential_conduction_velocity_m_per_s != 0.0
    assert result.spike_signal_to_noise_ratio_snr != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous High-Density CMOS M" in result.summary_report
