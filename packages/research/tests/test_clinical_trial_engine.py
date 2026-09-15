"""Tests for ClinicalTrialEngine (Phase 36)."""

import pytest
from research.clinical_trial_engine import ClinicalTrialEngine


def test_clinical_trial_engine_protocol_synthesis():
    engine = ClinicalTrialEngine()
    protocol = engine.synthesize_protocol(
        disease_indication="Familial Hypercholesterolemia",
        investigational_agent="LNP-Cas9-PCSK9",
        target_gene_or_protein="PCSK9",
        phase_type="Phase I/IIa",
    )

    assert "Familial Hypercholesterolemia" in protocol["protocol_title"]
    assert "LNP-Cas9-PCSK9" in protocol["protocol_title"]
    assert protocol["phase_type"] == "Phase I/IIa"
    assert len(protocol["cohort_criteria"]) >= 6
    assert any(c["criterion_type"] == "inclusion" for c in protocol["cohort_criteria"])
    assert any(c["criterion_type"] == "exclusion" for c in protocol["cohort_criteria"])
    assert protocol["sample_size_planned"] == 48
    assert protocol["adverse_risk_score"] > 0.0


def test_clinical_trial_engine_repurposing_screen():
    engine = ClinicalTrialEngine()
    candidates = engine.screen_repurposing_candidates(
        disease_indication="Familial Hypercholesterolemia",
        target_gene_or_protein="PCSK9",
    )

    assert len(candidates) >= 2
    assert all("compound_name" in c for c in candidates)
    assert all("binding_affinity_nm" in c for c in candidates)
    assert all("repurposing_rationale" in c for c in candidates)


def test_clinical_trial_engine_regulatory_package():
    engine = ClinicalTrialEngine()
    proto = engine.synthesize_protocol(
        disease_indication="Familial Hypercholesterolemia",
        investigational_agent="LNP-Cas9-PCSK9",
    )
    reg_pkg = engine.generate_regulatory_package(proto, regulatory_agency="FDA")

    assert reg_pkg["regulatory_agency"] == "FDA"
    assert reg_pkg["completeness_score"] >= 0.85
    assert reg_pkg["irb_readiness_verdict"] == "ready"
    assert "form_fda_1571" in reg_pkg["submission_checklist"]
