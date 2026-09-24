"""Tests for MembranePermeabilityEngine."""

from research.chemistry.membrane_permeability_engine import (
    MembranePermeabilityEngine,
    PAMPAEvaluationRequest,
)


def test_membrane_permeability_engine():
    engine = MembranePermeabilityEngine()
    req = PAMPAEvaluationRequest(
        molecule_name="Diazepam",
        smiles="CN1C(=O)CN=C(C2=C1C=CC(=C2)Cl)C3=CC=CC=C3",
        molecular_weight=284.74,
        logp=2.8,
        tpsa=32.67,
        h_bond_donors=0,
        h_bond_acceptors=3,
        rotatable_bonds=1,
    )
    res = engine.evaluate(req)
    assert res.status == "COMPLETED"
    assert res.papp_cm_per_s > 0
    assert res.permeability_class in ["High", "Moderate", "Low"]
    assert res.bbb_permeable is True
    assert len(res.diffusivity_profile) == 7
