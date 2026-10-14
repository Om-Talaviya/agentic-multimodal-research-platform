"""Tests for Phase 480: Autonomous Synthetic Protocellular Giant Unilamellar Vesicle (GUV) Electroformation Simulator."""

import pytest
from research.orchestration.guv_electroformation_dynamics_engine import GuvElectroformationDynamicsEngine


def test_guv_electroformation_dynamics_engine():
    engine = GuvElectroformationDynamicsEngine()
    result = engine.analyze(
        target_specimen="Indium Tin Oxide (ITO) Microelectrode Chamber with POPC/Cholesterol Bilayer Hydration",
        analytical_modality="guv-electroformation-dynamics",
        input_scale=1.0,
    )

    assert result.target_specimen == "Indium Tin Oxide (ITO) Microelectrode Chamber with POPC/Cholesterol Bilayer Hydration"
    assert result.confidence_score >= 0.95
    assert result.guv_mean_diameter_yield_um != 0.0
    assert result.bilayer_bending_rigidity_kbT != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Synthetic Protocell" in result.summary_report
