import pytest
from research.spatial.spatial_gnn_engine import (
    SpatialGNNNeighborhoodEngine,
    SpatialGNNInput,
)


def test_spatial_gnn_engine_matrix_generation():
    engine = SpatialGNNNeighborhoodEngine()
    result = engine.build_spatial_neighborhood_matrix(
        dataset_name="Xenium_PDAC_Cohort_12",
        tissue_type="Pancreatic Ductal Adenocarcinoma",
        radius_um=45.0,
    )

    assert result.dataset_name == "Xenium_PDAC_Cohort_12"
    assert result.tissue_type == "Pancreatic Ductal Adenocarcinoma"
    assert result.total_cells > 10000
    assert result.spatial_homophily_ratio > 0.5
    assert len(result.co_occurrence_edges) == 3
    assert len(result.spatial_niches) == 3
    assert len(result.ligand_receptor_networks) == 3
    assert len(result.recommendations) == 3
