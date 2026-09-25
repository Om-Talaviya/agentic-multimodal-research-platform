"""Tests for Phase 181: Rare Disease Deep Phenotyping Engine."""

import pytest
from research.clinical.rare_disease_hpo_phenotyping_engine import RareDiseaseHPOPhenotypingEngine


def test_rare_disease_hpo_phenotyping_simulation():
    engine = RareDiseaseHPOPhenotypingEngine()
    result = engine.analyze_clinical_phenotype(
        patient_cohort_id="PT-RD-8841",
        clinical_narrative="Tall stature, arachnodactyly, aortic root aneurysm, mitral valve prolapse, ectopia lentis",
    )

    assert result.patient_cohort_id == "PT-RD-8841"
    assert len(result.extracted_hpo_terms) == 5
    assert len(result.ranked_omim_matches) > 0
    assert result.top_disease_candidate == "Marfan Syndrome"
    assert result.causal_gene_symbol == "FBN1"
    assert result.diagnostic_confidence_pct > 70.0