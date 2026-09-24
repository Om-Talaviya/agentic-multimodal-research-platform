"""Tests for SpatialFluxEngine (Phase 150)."""

from research.metabolism.spatial_flux_engine import (
    SpatialFluxEngine,
    SpatialFluxRequest,
)


def test_spatial_flux_engine():
    engine = SpatialFluxEngine()
    req = SpatialFluxRequest(
        tissue_sample_id="TME-Renal-RCC",
        organ_context="Clear Cell Renal Cell Carcinoma",
        single_cells_count=3000,
        perfusion_radius_um=350.0,
    )
    result = engine.solve(req)
    assert result.single_cells_simulated == 3000
    assert result.mean_glycolytic_flux > 0
    assert len(result.pathway_fluxes) >= 4
    assert len(result.microdomains) >= 3
