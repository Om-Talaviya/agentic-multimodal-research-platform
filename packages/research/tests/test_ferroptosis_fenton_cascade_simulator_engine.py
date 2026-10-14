"""Tests for Phase 482: Autonomous Cellular Ferroptosis Lipid Peroxidation Fenton Reaction Cascade Simulator."""

import pytest
from research.orchestration.ferroptosis_fenton_cascade_simulator_engine import FerroptosisFentonCascadeSimulatorEngine


def test_ferroptosis_fenton_cascade_simulator_engine():
    engine = FerroptosisFentonCascadeSimulatorEngine()
    result = engine.analyze(
        target_specimen="GPX4-Inactivated HT-1080 Fibrosarcoma Spheroids with Labile Iron Pool Fe(II) Accumulation",
        analytical_modality="ferroptosis-fenton-cascade",
        input_scale=1.0,
    )

    assert result.target_specimen == "GPX4-Inactivated HT-1080 Fibrosarcoma Spheroids with Labile Iron Pool Fe(II) Accumulation"
    assert result.confidence_score >= 0.95
    assert result.lipid_hydroperoxide_accumulation_nmol_mg != 0.0
    assert result.labile_iron_pool_chelatable_uM != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Cellular Ferroptosi" in result.summary_report
