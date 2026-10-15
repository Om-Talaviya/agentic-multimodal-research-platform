"""Tests for Phase 528: Autonomous High-Speed Atomic Force Microscopy (HS-AFM) Myosin Motor Stepping Real-Time Profiler."""

import pytest
from research.orchestration.high_speed_afm_molecular_motor_dynamics_engine import HighSpeedAfmMolecularMotorDynamicsEngine


def test_high_speed_afm_molecular_motor_dynamics_engine():
    engine = HighSpeedAfmMolecularMotorDynamicsEngine()
    result = engine.analyze(
        target_specimen="Single Native Myosin V Dimer stepping along Immobilized Actin Filament in Microfluidic HS-AFM Cell",
        analytical_modality="hs-afm-molecular-motor",
        input_scale=1.0,
    )

    assert result.target_specimen == "Single Native Myosin V Dimer stepping along Immobilized Actin Filament in Microfluidic HS-AFM Cell"
    assert result.confidence_score >= 0.95
    assert result.hand_over_hand_step_distance_nm != 0.0
    assert result.power_stroke_lever_arm_rotation_deg != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous High-Speed Atomic F" in result.summary_report
