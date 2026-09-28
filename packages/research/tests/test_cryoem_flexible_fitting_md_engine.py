"""Tests for Phase 263: Autonomous In-Silico Cryo-EM Continuous Motion Trajectory & Flexible Molecular Dynamics Fitting Engine Engine."""

import pytest
from research.orchestration.cryoem_flexible_fitting_md_engine import CryoemFlexibleFittingMdEngine


def test_cryoem_flexible_fitting_md_engine():
    engine = CryoemFlexibleFittingMdEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="cryoem-flexible-fitting-md",
        input_scale=1.0,
    )
    assert getattr(result, "map_model_cross_correlation_score") != 0
    assert getattr(result, "ramachandran_favored_residue_pct") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
