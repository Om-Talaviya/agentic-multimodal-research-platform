"""Tests for Phase 429: Autonomous Whole-Cell Organelle Contact Site & Membrane Proximity Distance Transformer Repo."""

import pytest
from database.repositories.organelle_contact_site_proximity_repo import OrganelleContactSiteProximityRepository


@pytest.mark.asyncio
async def test_organelle_contact_site_proximity_repository(db_session):
    repo = OrganelleContactSiteProximityRepository(db_session)

    study = await repo.create_study(
        name="Study_429_Verification",
        target_specimen="Focused Ion Beam Scanning Electron Microscopy (FIB-SEM) Whole Cell",
        analytical_modality="organelle-contact-site",
        er_mitochondria_contact_distance_nm=14.2,
        contact_site_surface_area_um2=2.85,
        lipid_transfer_flux_rate=125.0,
        organelle_tethering_density=0.892,
        confidence_score=0.99,
        status="completed",
        summary_report="Phase 429 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_429_Verification"
    assert study.er_mitochondria_contact_distance_nm == 14.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="MAM_Contact_Microdomain_Mesh",
        profile_category="Primary Step",
        quantitative_value=14.2,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "MAM_Contact_Microdomain_Mesh"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="er_mitochondria_contact_distance_nm",
        observed_value=14.2,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 14.2

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_429_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
