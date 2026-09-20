"""
Unit tests for Phase 106: Spatial Lipidomics & Imaging MS Engine.
"""
import pytest
from research.spatial.lipidomics_engine import SpatialLipidomicsEngine

def test_lipid_maps_matching():
    engine = SpatialLipidomicsEngine()
    
    match = engine.match_lipid_species(760.585, tolerance_ppm=5.0)
    assert match is not None
    assert match["species"] == "PC(34:1)"
    assert match["class"] == "Phosphatidylcholine"

def test_spatial_colocalization():
    engine = SpatialLipidomicsEngine()
    
    # Identical maps -> correlation = 1.0
    map_a = [10.0, 20.0, 30.0, 40.0]
    map_b = [10.0, 20.0, 30.0, 40.0]
    corr = engine.compute_spatial_colocalization(map_a, map_b)
    assert corr == pytest.approx(1.0, abs=0.01)

    # Inverted maps -> correlation = -1.0
    map_c = [40.0, 30.0, 20.0, 10.0]
    inv_corr = engine.compute_spatial_colocalization(map_a, map_c)
    assert inv_corr == pytest.approx(-1.0, abs=0.01)

def test_process_spatial_dataset():
    engine = SpatialLipidomicsEngine()
    
    result = engine.process_dataset(
        sample_name="Brain-Slice-Test",
        tissue_type="Mouse Cortex",
        matrix_type="DHB",
        grid_dim=4
    )

    assert result["sample_name"] == "Brain-Slice-Test"
    assert len(result["lipid_species"]) == 5
    assert len(result["spatial_spots"]) == 5 * (4 * 4)  # 5 lipids * 16 spots
