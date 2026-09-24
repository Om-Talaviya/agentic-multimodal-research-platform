"""Tests for DNAOrigamiEngine (Phase 149)."""

from research.nanotech.dna_origami_engine import (
    DNAOrigamiEngine,
    DNAOrigamiDesignRequest,
)


def test_dna_origami_engine():
    engine = DNAOrigamiEngine()
    req = DNAOrigamiDesignRequest(
        nanorobot_name="Tumor Infiltrating Thrombin Box",
        geometry_type="Hollow Hexagonal Prism",
        target_biomarker="PD-L1",
        target_cargo_diameter_nm=10.0,
    )
    result = engine.design(req)
    assert result.staple_strands_count > 0
    assert result.folding_yield_percent > 80.0
    assert result.cargo_cavity_volume_nm3 > 0
    assert len(result.staple_strands) >= 3
    assert len(result.latch_mechanisms) >= 1
