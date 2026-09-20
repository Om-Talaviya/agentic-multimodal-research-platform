"""
Unit tests for Phase 105: HDX-MS Conformational Dynamics Engine.
"""
import pytest
from research.structural.hdx_engine import HDXDynamicsEngine

def test_hdx_uptake_calculation():
    engine = HDXDynamicsEngine()
    
    # Unprotected Apo peptide at short timepoint
    apo_res = engine.compute_fractional_uptake("MGTVSSRRA", timepoint_seconds=10.0, state_condition="APO")
    assert apo_res["fractional_uptake_pct"] > 0.0
    assert apo_res["deuterium_uptake_da"] > 0.0

    # Protected Ligand-Bound peptide shows lower exchange
    bound_res = engine.compute_fractional_uptake(
        "MGTVSSRRA",
        timepoint_seconds=10.0,
        state_condition="LIGAND_BOUND",
        binding_site_overlap=True
    )
    assert bound_res["fractional_uptake_pct"] < apo_res["fractional_uptake_pct"]
    assert bound_res["protection_factor_ln_p"] > apo_res["protection_factor_ln_p"]

def test_hdx_full_experiment_simulation():
    engine = HDXDynamicsEngine()
    peptides = [
        {"peptide_sequence": "MGTVSSRRA", "start_res": 1, "end_res": 9, "is_binding_site": False},
        {"peptide_sequence": "APGATNEKLFFL", "start_res": 10, "end_res": 21, "is_binding_site": True}
    ]

    sim = engine.simulate_experiment(
        protein_name="PCSK9",
        peptides=peptides,
        state_condition="LIGAND_BOUND"
    )

    assert sim["protein_name"] == "PCSK9"
    assert sim["total_peptides"] == 2
    assert sim["sequence_coverage_pct"] > 90.0
    assert len(sim["uptake_curves"]) == 10  # 2 peptides * 5 timepoints
    assert len(sim["protection_maps"]) == 21  # 21 residues covered
