"""Tests for Phase 481: Autonomous In-Situ Cryo-ET Ribosome Polysome Structural Topology & Nascent Chain Chaperone Coordinator Repo."""

import pytest
from database.repositories.cryoet_polysome_chaperone_topology_repo import CryoetPolysomeChaperoneTopologyRepository


@pytest.mark.asyncio
async def test_cryoet_polysome_chaperone_topology_repository(db_session):
    repo = CryoetPolysomeChaperoneTopologyRepository(db_session)

    study = await repo.create_study(
        name="Study_481_Verification",
        target_specimen="Vitrified Mammalian Reticulocyte Cytoplasm with Circular Polysome-Hsp70 Chaperone Ensembles",
        analytical_modality="cryoet-polysome-topology",
        inter_ribosomal_exit_channel_distance_nm=16.8,
        polysome_circularity_topology_index=0.885,
        chaperone_nascent_chain_occupancy_ratio=0.912,
        subtomogram_averaging_resolution_angstrom=5.25,
        confidence_score=0.993,
        status="completed",
        summary_report="Phase 481 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_481_Verification"
    assert study.inter_ribosomal_exit_channel_distance_nm == 16.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Exit_Site_Ribosome_Coupling_Helical_Ring",
        profile_category="Primary Step",
        quantitative_value=16.8,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Exit_Site_Ribosome_Coupling_Helical_Ring"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="inter_ribosomal_exit_channel_distance_nm",
        observed_value=16.8,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 16.8

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_481_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
