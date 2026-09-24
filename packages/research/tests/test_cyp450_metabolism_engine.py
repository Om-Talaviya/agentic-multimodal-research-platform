"""Tests for CYP450MetabolismEngine."""

from research.chemistry.cyp450_metabolism_engine import (
    CYP450MetabolismEngine,
    CYP450PredictionRequest,
)


def test_cyp450_metabolism_engine():
    engine = CYP450MetabolismEngine()
    req = CYP450PredictionRequest(
        compound_name="Midazolam",
        smiles="CC1=NC=C2N1C3=C(C=C(C=C3)Cl)C(=NC2)C4=CC=CC=C4F",
        molecular_weight=325.77,
        logp=3.1,
        aromatic_ring_count=3,
        basic_nitrogen_count=2,
    )
    res = engine.predict(req)
    assert res.status == "COMPLETED"
    assert res.clint_ml_min_kg > 0
    assert 0.0 < res.hepatic_extraction <= 1.0
    assert len(res.isoform_predictions) == 3
    assert len(res.clearance_curve) == 4
