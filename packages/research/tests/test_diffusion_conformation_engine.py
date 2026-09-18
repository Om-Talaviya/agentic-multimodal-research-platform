"""Tests for DiffusionConformationEngine."""
import pytest
from research.diffusion.diffusion_conformation_engine import DiffusionConformationEngine


def test_diffusion_conformation_docking():
    engine = DiffusionConformationEngine()
    result = engine.run_diffusion_docking(
        protein_pdb_id="6LU7",
        ligand_smiles="CC(=O)NC1=CC=C(O)C=C1",
        num_timesteps=500,
        model_variant="DiffDock_SE3",
        num_poses=5,
    )

    assert "job" in result
    assert result["job"]["protein_pdb_id"] == "6LU7"
    assert result["job"]["total_conformations_generated"] == 5
    assert result["job"]["best_confidence_score"] > 0.80

    assert "pocket_conformations" in result
    assert len(result["pocket_conformations"]) == 2
    for p in result["pocket_conformations"]:
        assert p["pocket_volume_angstrom3"] > 300.0
        assert p["cavity_druggability_score"] > 0.5

    assert "docking_poses" in result
    assert len(result["docking_poses"]) == 5
    for dp in result["docking_poses"]:
        assert dp["vina_affinity_score"] < -5.0
        assert dp["se3_confidence_score"] > 0.5
        assert "HETATM" in dp["ligand_coordinates_pdb"]
