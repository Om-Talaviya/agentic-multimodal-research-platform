"""Tests for Phase 468: Autonomous Synthetic Morphogenetic Morpho-Kinetic Boundary Sharpening & Eph-Ephrin Repulsion Engine Repo."""

import pytest
from database.repositories.eph_ephrin_morpho_repulsion_repo import EphEphrinMorphoRepulsionRepository


@pytest.mark.asyncio
async def test_eph_ephrin_morpho_repulsion_repository(db_session):
    repo = EphEphrinMorphoRepulsionRepository(db_session)

    study = await repo.create_study(
        name="Study_468_Verification",
        target_specimen="HEK293T EphB2/EphrinB1 Co-Culture Mosaic Boundary Array in Micropatterned Substrates",
        analytical_modality="eph-ephrin-morpho-repulsion",
        interface_roughness_boundary_width_um=6.8,
        eph_receptor_clustering_density_per_um2=420.0,
        contact_repulsion_retraction_velocity_um_min=2.45,
        heterotypic_sorting_order_parameter=0.945,
        confidence_score=0.99,
        status="completed",
        summary_report="Phase 468 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_468_Verification"
    assert study.interface_roughness_boundary_width_um == 6.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Bidirectional_EphB2_EphrinB1_Contact_Repulsion",
        profile_category="Primary Step",
        quantitative_value=6.8,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Bidirectional_EphB2_EphrinB1_Contact_Repulsion"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="interface_roughness_boundary_width_um",
        observed_value=6.8,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 6.8

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_468_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
