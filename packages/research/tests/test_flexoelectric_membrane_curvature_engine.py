"""Tests for Phase 473: Autonomous Bio-Piezoelectric Cell Membrane Flexoelectric Curvature Transduction Engine."""

import pytest
from research.orchestration.flexoelectric_membrane_curvature_engine import FlexoelectricMembraneCurvatureEngine


def test_flexoelectric_membrane_curvature_engine():
    engine = FlexoelectricMembraneCurvatureEngine()
    result = engine.analyze(
        target_specimen="Asymmetric Phospholipid Bilayer Giant Unilamellar Vesicle with Micropipette Aspiration Curvature",
        analytical_modality="flexoelectric-membrane-curvature",
        input_scale=1.0,
    )

    assert result.target_specimen == "Asymmetric Phospholipid Bilayer Giant Unilamellar Vesicle with Micropipette Aspiration Curvature"
    assert result.confidence_score >= 0.95
    assert result.flexoelectric_coupling_coefficient_pC_per_m != 0.0
    assert result.membrane_curvature_radius_nm != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Bio-Piezoelectric C" in result.summary_report
