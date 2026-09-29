"""Tests for Phase 338: Autonomous Multi-Omics Spatial Cell-Cell Interaction & Ligand-Receptor Tensor Decomposition Core Engine."""

import pytest
from research.orchestration.spatial_tensor_cci_decomposition_engine import SpatialTensorCciDecompositionEngine


def test_spatial_tensor_cci_decomposition_engine():
    engine = SpatialTensorCciDecompositionEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="spatial-tensor-cci",
        input_scale=1.0,
    )
    assert getattr(result, "tensor_factorization_reconstruction_fidelity_pct") != 0
    assert getattr(result, "ligand_receptor_spatial_colocalization_score") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
