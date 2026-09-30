"""Tests for Phase 406: Autonomous 3D Organoid Perfusable Microfluidic Endothelial Vasculature Simulator Engine."""

import pytest
from research.orchestration.organoid_microfluidic_vasculature_engine import OrganoidMicrofluidicVasculatureEngine


def test_organoid_microfluidic_vasculature_engine():
    engine = OrganoidMicrofluidicVasculatureEngine()
    result = engine.analyze(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="organoid-microfluidic-vasculature",
        input_scale=1.0,
    )

    assert result.target_specimen == "Human Patient Cohort Sample"
    assert result.confidence_score >= 0.95
    assert getattr(result, "vascular_perfusion_lumen_patency_pct") > 0
    assert getattr(result, "fluid_shear_stress_endothelial_alignment_dyn_cm2") > 0
    assert len(result.item_profiles) == 3
    assert len(result.metric_traces) == 3
    assert "Phase 406" in result.summary_report
