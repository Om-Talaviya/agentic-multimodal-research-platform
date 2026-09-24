"""Tests for OrganoidMorphometryEngine (Phase 147)."""

from research.imaging.organoid_morphometry_engine import (
    OrganoidMorphometryEngine,
    OrganoidAnalysisRequest,
)


def test_organoid_morphometry_engine():
    engine = OrganoidMorphometryEngine()
    req = OrganoidAnalysisRequest(
        study_name="Pancreatic Spheroid Assay",
        tumor_type="PDAC",
        z_slices_count=5,
        primary_compound="Gemcitabine",
        compound_dose_uM=2.0,
    )
    result = engine.analyze(req)
    assert result.mean_diameter_um > 0
    assert result.mean_volume_um3 > 0
    assert 0.0 < result.sphericity_index <= 1.0
    assert len(result.z_slices) == 5
    assert len(result.dose_responses) == 1
