"""Tests for Phase 495: Autonomous Spatial Multi-Modal Epigenomic CUT&Tag-RNA Joint Profiling Diffusion Trajectory Mapper Repo."""

import pytest
from database.repositories.cuttag_rna_joint_diffusion_trajectory_repo import CuttagRnaJointDiffusionTrajectoryRepository


@pytest.mark.asyncio
async def test_cuttag_rna_joint_diffusion_trajectory_repository(db_session):
    repo = CuttagRnaJointDiffusionTrajectoryRepository(db_session)

    study = await repo.create_study(
        name="Study_495_Verification",
        target_specimen="Developing Murine Cortical Plate Radial Glia Lineage with H3K4me3 / H3K27ac and mRNA Co-Assay",
        analytical_modality="cuttag-rna-joint-diffusion",
        epigenomic_chromatin_velocity_coherence=0.932,
        promoter_enhancer_concordance_score=0.895,
        diffusion_pseudotime_lineage_resolution_tau=0.965,
        joint_latent_space_neighbor_overlap_pct=94.2,
        confidence_score=0.992,
        status="completed",
        summary_report="Phase 495 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_495_Verification"
    assert study.epigenomic_chromatin_velocity_coherence == 0.932

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Radial_Glia_To_Neuron_Chromatin_Opening_Trajectory",
        profile_category="Primary Step",
        quantitative_value=0.932,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Radial_Glia_To_Neuron_Chromatin_Opening_Trajectory"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="epigenomic_chromatin_velocity_coherence",
        observed_value=0.932,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.932

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_495_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
