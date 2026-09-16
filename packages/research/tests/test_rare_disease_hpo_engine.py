"""
Tests for Phase 61: Rare Disease HPO Engine.
"""
from research.hpo.rare_disease_hpo_engine import RareDiseaseHPOEngine


def test_match_case_phenotypes():
    res = RareDiseaseHPOEngine.match_case_phenotypes(
        [
            {"hpo_id": "HP:0001250", "term_name": "Seizures"},
            {"hpo_id": "HP:0001263", "term_name": "Developmental delay"},
        ]
    )
    assert "phenotypes" in res
    assert "candidate_genes" in res
    assert len(res["candidate_genes"]) >= 3
    assert res["candidate_genes"][0]["is_top_match"] is True
