"""
Tests for Phase 57: Spatial Metabolomics Engine.
"""
from research.metabolomics.spatial_metabolomics_engine import SpatialMetabolomicsEngine


def test_simulate_spatial_metabolome():
    res = SpatialMetabolomicsEngine.simulate_spatial_metabolome(
        sample_id="TEST-MALDI",
        organ_type="Liver Section",
    )
    assert "metabolites" in res
    assert "flux_routes" in res
    assert len(res["metabolites"]) >= 5
    assert len(res["flux_routes"]) >= 4
