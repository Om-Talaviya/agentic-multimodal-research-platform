"""Tests for Phase 540: Autonomous Diamond Nitrogen-Vacancy (NV) Center Quantum Defect Intracellular Thermal & Magnetic Sensor."""

import pytest
from research.orchestration.single_molecule_quantum_defect_spin_sensor_engine import SingleMoleculeQuantumDefectSpinSensorEngine


def test_single_molecule_quantum_defect_spin_sensor_engine():
    engine = SingleMoleculeQuantumDefectSpinSensorEngine()
    result = engine.analyze(
        target_specimen="Fluorescent Nanodiamond with Single NV- Spin Defect internalized in Living Single Macrophage Cell",
        analytical_modality="nv-center-quantum-sensing",
        input_scale=1.0,
    )

    assert result.target_specimen == "Fluorescent Nanodiamond with Single NV- Spin Defect internalized in Living Single Macrophage Cell"
    assert result.confidence_score >= 0.95
    assert result.magnetic_field_sensitivity_nT_sqrt_hz != 0.0
    assert result.intracellular_thermal_sensitivity_mK_sqrt_hz != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Diamond Nitrogen-Va" in result.summary_report
