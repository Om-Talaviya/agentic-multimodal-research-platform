"""Tests for Phase 573: Autonomous Equivariant SE(3) Diffusion Deep Learning Protein-Protein Interaction (PPI) Complex Docking & Binding Affinity Forecaster."""

import pytest
from research.orchestration.deep_learning_protein_protein_docking_affinity_engine import DeepLearningProteinProteinDockingAffinityEngine


def test_deep_learning_protein_protein_docking_affinity_engine():
    engine = DeepLearningProteinProteinDockingAffinityEngine()
    result = engine.analyze(
        target_specimen="SARS-CoV-2 Spike Receptor-Binding Domain Complexed with Engineered Nanobody Nb21-Fc Variant",
        analytical_modality="se3-diffusion-ppi-docking",
        input_scale=1.0,
    )
    assert result is not None
    assert result.interface_rmsd_angstrom != 0.0
    assert result.binding_free_energy_delta_g_kcal_mol != 0.0
    assert result.docking_pose_confidence_plddt != 0.0
    assert result.buried_surface_area_angstrom2 != 0.0
    assert result.confidence_score >= 0.90
    assert len(result.item_profiles) == 3
    assert len(result.metric_traces) == 3
    assert result.target_specimen == "SARS-CoV-2 Spike Receptor-Binding Domain Complexed with Engineered Nanobody Nb21-Fc Variant"
    assert result.analytical_modality == "se3-diffusion-ppi-docking"
