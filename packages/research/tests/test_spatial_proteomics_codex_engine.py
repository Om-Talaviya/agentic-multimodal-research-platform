"""Tests for CODEXSpatialProteomicsEngine (Phase 155)."""

from research.spatial.codex_spatial_proteomics_engine import (
    CODEXSpatialProteomicsEngine,
    SpatialProteomicsCODEXRequest,
)


def test_spatial_proteomics_codex_engine():
    engine = CODEXSpatialProteomicsEngine()
    req = SpatialProteomicsCODEXRequest(
        tissue_sample_name="Colorectal Carcinoma Section",
        organ_tissue_type="Colon Mucosa",
        panel_plex_level=40,
        single_cells_estimate=9000,
    )
    result = engine.process_multiplex_panel(req)
    assert result.single_cells_segmented == 9000
    assert result.mean_signal_to_background > 10.0
    assert len(result.marker_expressions) >= 5
    assert len(result.neighborhood_phenotypes) >= 3
