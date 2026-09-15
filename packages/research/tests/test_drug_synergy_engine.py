"""Unit tests for Drug Synergy Engine (Phase 45)."""
import pytest
from research.drug_synergy_engine import DrugSynergyEngine

def test_drug_synergy_engine():
    engine = DrugSynergyEngine(seed=123)

    res = engine.run_repurposing_screen(disease_indication="Sorafenib-Resistant HCC", n_candidates=3)
    assert "candidates" in res
    assert "synergies" in res
    assert len(res["candidates"]) == 3
    assert res["candidates"][0]["connectivity_score"] < -0.7
    assert len(res["synergies"]) >= 2
    assert res["synergies"][0]["zip_synergy_score"] > 10.0
