import pytest
from research.toxicity.toxicity_engine import QSARToxicityEngine

def test_toxicity_qsar_engine():
    engine = QSARToxicityEngine()

    # 1. Test Ames and hERG prediction on safe molecule
    clean_smiles = "CC(=O)Oc1ccccc1C(=O)O"  # Aspirin
    res = engine.predict_compound_toxicity(clean_smiles, "Aspirin", 180.2, 1.2)
    assert res["ames_mutagenicity_status"] == "NEGATIVE"
    assert res["herg_cardiotox_risk"] == "LOW"
    assert res["dili_hepatotox_risk"] == "LOW"
    assert res["ld50_rat_mg_kg"] > 500.0

    # 2. Test Reactive Alert (Epoxide)
    epoxide_smiles = "C1OC1c2ccccc2"
    res_epoxide = engine.predict_compound_toxicity(epoxide_smiles, "Styrene-Oxide", 120.1, 1.6)
    assert any("Epoxide" in a["alert_name"] for a in res_epoxide["structural_alerts"])
    assert res_epoxide["ames_mutagenicity_status"] == "POSITIVE"
