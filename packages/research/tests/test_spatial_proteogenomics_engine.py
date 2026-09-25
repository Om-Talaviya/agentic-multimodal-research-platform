"""Tests for Spatial Proteogenomics Engine."""

import pytest
from research.spatial.spatial_proteogenomics_engine import SpatialProteogenomicsEngine


def test_spatial_proteogenomics_engine_analysis() -> None:
    engine = SpatialProteogenomicsEngine()
    result = engine.run_spatial_proteogenomic_analysis(
        study_name="GBM Spatial CITE-seq Analysis",
        tissue_sample_id="GBM_TME_Slice_04",
    )

    assert result["study_name"] == "GBM Spatial CITE-seq Analysis"
    assert result["tissue_sample_id"] == "GBM_TME_Slice_04"
    assert result["total_spots_analyzed"] == 4
    assert result["mean_pearson_colocalization_r"] > 0.80
    assert result["subcellular_niche_count"] >= 3
    assert len(result["spots"]) == 4
    assert len(result["enrichment_metrics"]) >= 4

    # Check spot details
    first_spot = result["spots"][0]
    assert "spot_barcode" in first_spot
    assert "mrna_normalized_count" in first_spot
    assert "protein_adt_signal" in first_spot
    assert "colocalization_pearson_r" in first_spot
