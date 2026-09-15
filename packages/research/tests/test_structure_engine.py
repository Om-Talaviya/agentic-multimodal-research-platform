"""
Tests for StructurePredictionEngine.
"""

import pytest
from research.structure_engine import StructurePredictionEngine


def test_predict_structure_alphafold3():
    engine = StructurePredictionEngine()
    sequence = "MKTIIALSYIFCLVFA"
    result = engine.predict_structure(
        uniprot_id="Q9BYF1",
        gene_name="PCSK9",
        sequence=sequence,
        structure_source="AlphaFold3",
    )

    assert result.uniprot_id == "Q9BYF1"
    assert result.gene_name == "PCSK9"
    assert result.structure_source == "AlphaFold3"
    assert result.mean_plddt_score >= 50.0
    assert "ATOM" in result.pdb_coordinate_data
    assert "END" in result.pdb_coordinate_data
    assert len(result.binding_pockets) >= 1
    assert "alpha_helix_pct" in result.secondary_structure_summary


def test_evaluate_docking():
    engine = StructurePredictionEngine()
    pred = engine.predict_structure(uniprot_id="Q9BYF1")

    pocket = pred.binding_pockets[0]
    docking = engine.evaluate_docking(
        pocket=pocket,
        ligand_name="Evolocumab Mimetic",
        ligand_smiles="CC(=O)NC1=CC=C(O)C=C1",
    )

    assert docking.ligand_name == "Evolocumab Mimetic"
    assert docking.binding_affinity_kcal_mol < 0.0  # Favorable binding
    assert docking.hydrogen_bonds_count >= 1
    assert docking.rmsd_angstrom > 0.0


def test_scan_mutational_stability():
    engine = StructurePredictionEngine()

    scan = engine.scan_mutational_stability(
        wildtype_residue="D",
        position=374,
        mutant_residue="Y",
    )

    assert scan.wildtype_residue == "D"
    assert scan.position == 374
    assert scan.mutant_residue == "Y"
    assert scan.stability_verdict in ["stabilizing", "destabilizing", "neutral"]
    assert scan.delta_delta_g_kcal_mol < 0.0  # D374Y gain of function
    assert scan.pathogenicity_score >= 0.8
