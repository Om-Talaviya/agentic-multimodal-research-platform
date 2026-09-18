"""Tests for PreclinicalToxicologyEngine."""

import pytest
from research.toxicology.toxicogenomics_engine import PreclinicalToxicologyEngine


def test_preclinical_toxicology_engine_assessment():
    engine = PreclinicalToxicologyEngine()
    assessment = engine.assess_compound_safety(
        compound_name="Imatinib",
        smiles="CC1=C(C=C(C=C1)NC(=O)C2=CC=C(C=C2)CN3CCN(CC3)C)NC4=NC=CC(=N4)C5=CN=CC=C5",
    )
    assert assessment["compound_name"] == "Imatinib"
    assert 0.0 <= assessment["therapeutic_safety_index"] <= 100.0
    assert assessment["overall_safety_tier"] in ["FAVORABLE", "MODERATE_RISK", "HIGH_RISK", "CRITICAL"]
    assert len(assessment["endpoints"]) >= 5
    assert "risk_summary" in assessment
    assert assessment["plasma_protein_binding_pct"] > 0.0


def test_preclinical_toxicology_alert_detection():
    engine = PreclinicalToxicologyEngine()
    # Nitroaromatic compound should trigger alert
    assessment = engine.assess_compound_safety(
        compound_name="4-Nitroaniline",
        smiles="c1cc(ccc1N)[N+](=O)[O-]",
    )
    assert len(assessment["structural_tox_alerts"]) > 0
    assert any("Nitro" in a["name"] for a in assessment["structural_tox_alerts"])
