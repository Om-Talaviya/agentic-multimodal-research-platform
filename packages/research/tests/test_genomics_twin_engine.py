"""Tests for ClinicalGenomicsTwinEngine."""
import pytest
from research.clinical.genomics_twin_engine import ClinicalGenomicsTwinEngine


def test_genomics_twin_engine_poor_metabolizer():
    engine = ClinicalGenomicsTwinEngine()
    result = engine.evaluate_patient_twin(
        patient_mrn="MRN-TEST-01",
        diplotypes={"CYP2C19": "*2/*2", "CYP2D6": "*4/*4"},
        target_drug="Clopidogrel",
        prescribed_dose_mg=75.0,
    )

    assert "profile" in result
    assert result["profile"]["patient_mrn"] == "MRN-TEST-01"
    assert result["profile"]["high_risk_drug_interactions_count"] == 2

    assert "guidelines" in result
    assert len(result["guidelines"]) == 2
    phenotypes = [g["metabolizer_phenotype"] for g in result["guidelines"]]
    assert "POOR_METABOLIZER" in phenotypes

    assert "twin_simulations" in result
    sim = result["twin_simulations"][0]
    assert sim["drug_administered"] == "Clopidogrel"
    assert sim["toxic_accumulation_risk"] == "HIGH"
    assert "Prasugrel" in sim["alternate_drug_suggestion"]


def test_genomics_twin_engine_normal_metabolizer():
    engine = ClinicalGenomicsTwinEngine()
    result = engine.evaluate_patient_twin(
        patient_mrn="MRN-TEST-02",
        diplotypes={"CYP2C19": "*1/*1", "CYP2D6": "*1/*1"},
        target_drug="Clopidogrel",
    )

    assert result["profile"]["high_risk_drug_interactions_count"] == 0
    sim = result["twin_simulations"][0]
    assert sim["toxic_accumulation_risk"] == "LOW"
    assert sim["recommended_adjusted_dose_mg"] == 75.0
