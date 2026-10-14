"""Tests for Phase 519: Autonomous Non-Equilibrium Active Matter Cytoskeletal Topological Defect Self-Propulsion Simulator."""

import pytest
from research.orchestration.active_matter_cytoskeletal_nematic_defect_engine import ActiveMatterCytoskeletalNematicDefectEngine


def test_active_matter_cytoskeletal_nematic_defect_engine():
    engine = ActiveMatterCytoskeletalNematicDefectEngine()
    result = engine.analyze(
        target_specimen="Microtubule-Kinesin Active Gel Nematic Liquid Crystal Layer at Oil-Water Interface",
        analytical_modality="active-nematic-matter-dynamics",
        input_scale=1.0,
    )

    assert result.target_specimen == "Microtubule-Kinesin Active Gel Nematic Liquid Crystal Layer at Oil-Water Interface"
    assert result.confidence_score >= 0.95
    assert result.topological_defect_annihilation_rate_s_inv != 0.0
    assert result.active_turbulent_vortex_correlation_length_um != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Non-Equilibrium Act" in result.summary_report
