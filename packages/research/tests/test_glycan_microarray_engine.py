"""Tests for GlycanMicroarrayEngine (Phase 148)."""

from research.glycomics.glycan_microarray_engine import (
    GlycanMicroarrayEngine,
    GlycanScreenRequest,
)


def test_glycan_microarray_engine():
    engine = GlycanMicroarrayEngine()
    req = GlycanScreenRequest(
        target_lectin_name="Wheat Germ Agglutinin (WGA)",
        organism_source="Triticum vulgaris",
        concentration_ug_ml=5.0,
    )
    result = engine.analyze(req)
    assert result.spots_evaluated == 5
    assert result.kd_apparent_nM > 0
    assert len(result.top_binding_spots) == 5
    assert len(result.motif_enrichments) == 3
