"""Tests for Phase 431: Autonomous High-Plex Spatial Transcriptomics Spot Deconvolution & Cell-Type Niche Interaction Engine Repo."""

import pytest
from database.repositories.spatial_transcriptomics_niche_deconvolution_repo import SpatialTranscriptomicsNicheDeconvolutionRepository


@pytest.mark.asyncio
async def test_spatial_transcriptomics_niche_deconvolution_repository(db_session):
    repo = SpatialTranscriptomicsNicheDeconvolutionRepository(db_session)

    study = await repo.create_study(
        name="Study_431_Verification",
        target_specimen="10x Visium HD Formalin-Fixed Paraffin-Embedded Tissue Slice",
        analytical_modality="spatial-niche-deconvolution",
        sub_spot_cell_type_purity=0.942,
        niche_cross_talk_significance_p=0.0008,
        ligand_receptor_spatial_correlation=0.865,
        microenvironment_entropy_index=1.42,
        confidence_score=0.989,
        status="completed",
        summary_report="Phase 431 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_431_Verification"
    assert study.sub_spot_cell_type_purity == 0.942

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Sub_Spot_Cellular_Density_Deconvolution",
        profile_category="Primary Step",
        quantitative_value=0.942,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Sub_Spot_Cellular_Density_Deconvolution"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="sub_spot_cell_type_purity",
        observed_value=0.942,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.942

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_431_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
