"""
Tests for Phase 60: Nanomedicine PBPK Engine.
"""
from research.pbpk.pbpk_engine import NanomedicinePBPKEngine


def test_simulate_pbpk():
    res = NanomedicinePBPKEngine.simulate_pbpk(
        formulation_name="LNP-01",
        diameter_nm=85.0,
        zeta_mv=-3.5,
        peg_pct=1.5,
        dose_mg_kg=1.0,
        epr_index=0.85,
    )
    assert "compartments" in res
    assert "clearance_pathways" in res
    assert len(res["compartments"]) == 7
    assert len(res["clearance_pathways"]) >= 3
