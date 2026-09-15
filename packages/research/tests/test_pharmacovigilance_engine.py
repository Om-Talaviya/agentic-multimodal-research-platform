"""Tests for Pharmacovigilance Engine (Phase 49)."""
from research.pharmacovigilance_engine import PharmacovigilanceEngine

def test_pharmacovigilance_engine():
    engine = PharmacovigilanceEngine()
    res = engine.detect_signals(
        drug_name="Trastuzumab Deruxtecan",
        total_corpus_reports=1250000
    )
    assert len(res["signals"]) == 3
    sig = res["signals"][0]
    assert sig["metrics"]["prr"] > 2.0
    assert sig["metrics"]["ic025"] > 0.0
    assert sig["who_umc_causality"] in ["Certain", "Probable", "Possible"]
