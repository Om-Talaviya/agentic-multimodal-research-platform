"""Unit tests for Generative Chemistry Engine (Phase 43)."""
import pytest
from research.generative_chemistry_engine import GenerativeChemistryEngine

def test_generative_chemistry_engine():
    engine = GenerativeChemistryEngine(seed=123)

    mols = engine.generate_small_molecules(target_protein="PCSK9", n_candidates=4)
    assert len(mols) == 4
    assert mols[0]["target_protein"] == "PCSK9"
    assert "smiles" in mols[0]
    assert mols[0]["qed_score"] > 0.6
    assert mols[0]["predicted_binding_affinity"] < -8.0
    assert "admet" in mols[0]

    abs_list = engine.optimize_antibody_cdr(antigen_target="HER2", n_mutants=3)
    assert len(abs_list) == 3
    assert abs_list[0]["antigen_target"] == "HER2"
    assert len(abs_list[0]["cdr_h3_sequence"]) > 5
    assert abs_list[0]["kd_affinity_nm"] > 0.0
