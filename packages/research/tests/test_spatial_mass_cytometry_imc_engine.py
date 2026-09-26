"""Tests for Phase 221: Autonomous Spatial Imaging Mass Cytometry (IMC) 40-Plex Phenotyping & Microenvironment Niche Ranker Engine Engine."""

import pytest
from research.orchestration.spatial_mass_cytometry_imc_engine import SpatialMassCytometryImcEngine


def test_spatial_mass_cytometry_imc_engine():
    engine = SpatialMassCytometryImcEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="spatial-mass-cytometry-imc",
        input_scale=1.0,
    )
    assert getattr(result, "segmentation_f1_score") != 0
    assert getattr(result, "phenotypic_purity_pct") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
