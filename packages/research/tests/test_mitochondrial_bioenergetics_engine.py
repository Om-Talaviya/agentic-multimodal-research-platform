"""Tests for MitochondrialBioenergeticsEngine."""

from research.cellular.mitochondrial_bioenergetics_engine import (
    MitochondrialBioenergeticsEngine,
    BioenergeticsSimulationRequest,
)


def test_mitochondrial_bioenergetics_engine():
    engine = MitochondrialBioenergeticsEngine()
    req = BioenergeticsSimulationRequest(
        cell_line="HepG2 Hepatocytes",
        substrate_type="Pyruvate/Malate",
        uncoupler_fccp_concentration_um=1.0,
        complex_i_inhibition_pct=25.0,
    )
    res = engine.simulate(req)
    assert res.status == "COMPLETED"
    assert res.basal_ocr_pmol_min > 0
    assert res.maximal_respiratory_capacity > res.basal_ocr_pmol_min
    assert len(res.etc_complexes) == 5
