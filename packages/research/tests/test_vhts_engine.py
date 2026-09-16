"""Unit tests for VirtualHTSEngine (Phase 54)."""
import pytest
from research.vhts.vhts_engine import VirtualHTSEngine


def test_vhts_engine_docking_pose_evaluation():
    engine = VirtualHTSEngine()

    # 1. Evaluate clean molecule
    smiles = "CC(C)N1CCN(CC1)c2cc3ncccc3nc2Nc4ccc(F)cc4"
    result = engine.evaluate_docking_pose(
        smiles=smiles,
        target_pdb_id="7L11",
        pocket_box={"center": [0, 0, 0], "size": [20, 20, 20]},
    )

    assert result["docking_score_kcal_mol"] < -7.0
    assert result["estimated_kd_nm"] > 0
    assert result["pains_filter_passed"] is True

    # 2. Evaluate PAINS alert molecule
    pains_smiles = "O=C1NC(=S)SC1=Cc2ccccc2"  # Rhodanine derivative
    pains_result = engine.evaluate_docking_pose(
        smiles="rhodanine_derivative_test",
        target_pdb_id="7L11",
        pocket_box={},
    )
    assert pains_result["pains_filter_passed"] is False


def test_vhts_engine_hit_clustering():
    engine = VirtualHTSEngine()

    sample_hits = [
        {"docking_score_kcal_mol": -11.5},
        {"docking_score_kcal_mol": -10.8},
        {"docking_score_kcal_mol": -9.9},
    ]
    clusters = engine.cluster_hits(sample_hits, num_clusters=3)
    assert len(clusters) == 3
    for c in clusters:
        assert "cluster_label" in c
        assert "mean_affinity_kcal_mol" in c
