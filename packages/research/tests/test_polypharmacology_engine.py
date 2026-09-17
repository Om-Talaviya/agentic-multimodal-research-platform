"""Tests for Chemogenomics Polypharmacology Engine."""
import pytest
from research.chemogenomics.polypharmacology_engine import ChemogenomicsPolypharmacologyEngine


def test_screen_compound_selective():
    engine = ChemogenomicsPolypharmacologyEngine()
    compound_input = {
        "compound_name": "Osimertinib",
        "smiles": "COC1=C(C=C2C(=C1)N=CN=C2NC3=CC(=C(C=C3)NC(=O)C=C)N(C)CCN(C)C)OC",
        "primary_target": "EGFR",
    }
    affinities = [
        {"target_gene": "EGFR", "uniprot_id": "P00533", "affinity_type": "IC50", "affinity_value_nm": 1.5, "is_primary_target": True},
        {"target_gene": "ERBB2", "uniprot_id": "P04626", "affinity_type": "IC50", "affinity_value_nm": 350.0, "is_primary_target": False},
        {"target_gene": "SRC", "uniprot_id": "P12931", "affinity_type": "IC50", "affinity_value_nm": 15000.0, "is_primary_target": False},
    ]

    result = engine.screen_compound(compound_input, affinities)
    assert result["gini_selectivity_index"] >= 0.20
    assert result["selectivity_tier"] in ["HIGHLY_SELECTIVE", "FAMILY_SELECTIVE", "PAN_INHIBITOR"]
    assert len(result["affinities"]) == 3


def test_screen_compound_antitarget_herg_alert():
    engine = ChemogenomicsPolypharmacologyEngine()
    compound_input = {
        "compound_name": "Cardiotoxic Candidate X",
        "smiles": "CCC1=CC=CC=C1",
        "primary_target": "Target A",
    }
    affinities = [
        {"target_gene": "Target A", "uniprot_id": "P11111", "affinity_type": "IC50", "affinity_value_nm": 10.0, "is_primary_target": True},
        {"target_gene": "KCNH2", "uniprot_id": "Q12809", "affinity_type": "IC50", "affinity_value_nm": 450.0, "is_primary_target": False},
    ]

    result = engine.screen_compound(compound_input, affinities)
    assert result["off_target_liabilities_count"] >= 1
    assert any(al["risk_type"] == "CARDIOTOXICITY_HERG" for al in result["alerts"])
