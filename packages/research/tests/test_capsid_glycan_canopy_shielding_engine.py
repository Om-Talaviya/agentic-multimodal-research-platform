"""Tests for Phase 335: Autonomous Viral Capsid Cryo-EM Surface Epitope Shielding & Glycan Canopy Modeler Engine."""

import pytest
from research.orchestration.capsid_glycan_canopy_shielding_engine import CapsidGlycanCanopyShieldingEngine


def test_capsid_glycan_canopy_shielding_engine():
    engine = CapsidGlycanCanopyShieldingEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="capsid-glycan-canopy",
        input_scale=1.0,
    )
    assert getattr(result, "epitope_solvent_accessible_surface_shielding_pct") != 0
    assert getattr(result, "neutralizing_antibody_steric_clash_score") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
