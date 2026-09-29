"""Tests for Phase 338: Autonomous Multi-Omics Spatial Cell-Cell Interaction & Ligand-Receptor Tensor Decomposition Core Repo."""

import pytest
from database.repositories.spatial_tensor_cci_decomposition_repo import SpatialTensorCciDecompositionRepository


@pytest.mark.asyncio
async def test_spatial_tensor_cci_decomposition_repository(db_session):
    repo = SpatialTensorCciDecompositionRepository(db_session)

    study = await repo.create_study(
        name="Study_338_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="spatial-tensor-cci",
        tensor_factorization_reconstruction_fidelity_pct=97.3,
        ligand_receptor_spatial_colocalization_score=18.5,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 338 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_338_Verification"
    assert getattr(study, "tensor_factorization_reconstruction_fidelity_pct") == 97.3

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Pancreatic_Ductal_Adenocarcinoma_Stroma_Immune_Tensor_Field",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Pancreatic_Ductal_Adenocarcinoma_Stroma_Immune_Tensor_Field"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="Sensitivity & Recovery Rate",
        observed_value=0.984,
        z_score=2.85,
        p_value=0.00012,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.984

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_338_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
