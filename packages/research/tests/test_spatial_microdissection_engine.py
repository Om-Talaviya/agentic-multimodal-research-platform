"""
Engine tests for Phase 162: Spatial Microdissection & Subcellular Spot Deconvolution.
"""

from research.spatial.spatial_microdissection_engine import SpatialMicrodissectionEngine


def test_spatial_microdissection_engine():
    engine = SpatialMicrodissectionEngine()
    result = engine.deconvolve_spatial_spots(
        sample_name="VisiumHD_Ovarian_Cancer",
        tissue_type="High-Grade Serous Ovarian Carcinoma",
        spot_grid_size=4,
        resolution_nm=80.0,
    )

    assert result.sample_name == "VisiumHD_Ovarian_Cancer"
    assert result.total_spots == 16
    assert result.resolution_nm == 80.0
    assert result.mean_entropy > 0.0
    assert len(result.spots) == 16
    assert len(result.niches) == 2
    assert len(result.recommendations) >= 2
