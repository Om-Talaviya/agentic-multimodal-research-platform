"""Tests for Phase 214: Autonomous Cryo-EM Continuous Flexible Backbone Motion & Deep Non-Rigid Fitting Engine Engine."""

import pytest
from research.orchestration.cryoem_flexible_backbone_refine_engine import CryoEMFlexibleBackboneRefineEngine


def test_cryoem_flexible_backbone_refine_engine():
    engine = CryoEMFlexibleBackboneRefineEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="cryoem-flexible-backbone-refine",
        input_scale=1.0,
    )
    assert getattr(result, "density_cross_correlation") != 0
    assert getattr(result, "backbone_rmsd_angstrom") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
