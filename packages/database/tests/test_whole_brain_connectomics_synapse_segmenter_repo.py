"""Tests for Phase 563: Autonomous Whole-Brain Nanoscale Connectomics Automated Volume Electron Microscopy Synapse Segmenter Repo."""

import pytest
from database.repositories.whole_brain_connectomics_synapse_segmenter_repo import WholeBrainConnectomicsSynapseSegmenterRepository


@pytest.mark.asyncio
async def test_whole_brain_connectomics_synapse_segmenter_repository(db_session):
    repo = WholeBrainConnectomicsSynapseSegmenterRepository(db_session)

    study = await repo.create_study(
        name="Study_563_Verification",
        target_specimen="Serial Section Electron Tomography (FIB-SEM) of Adult Drosophila Melanogaster Central Brain at 4x4x4 nm3 Voxel Resolution",
        analytical_modality="whole-brain-connectomics-segmentation",
        synaptic_junction_detection_f1_score=0.982,
        t_bar_active_zone_reconstruction_precision=0.978,
        neurite_skeletonization_topological_accuracy=0.991,
        segmented_synaptic_density_per_100_um3=84.0,
        confidence_score=0.997,
        status="completed",
        summary_report="Phase 563 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_563_Verification"
    assert study.synaptic_junction_detection_f1_score == 0.982

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Presynaptic_TBar_Vesicle_Release_Site_Mesh",
        profile_category="Primary Step",
        quantitative_value=0.982,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Presynaptic_TBar_Vesicle_Release_Site_Mesh"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="synaptic_junction_detection_f1_score",
        observed_value=0.982,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.982

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_563_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
