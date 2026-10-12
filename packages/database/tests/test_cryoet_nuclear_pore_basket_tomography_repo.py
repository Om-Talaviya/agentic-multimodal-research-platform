"""Tests for Phase 438: Autonomous Cryo-ET In-Situ Nuclear Pore Complex (NPC) Nuclear Basket Dynamic Conformation Engine Repo."""

import pytest
from database.repositories.cryoet_nuclear_pore_basket_tomography_repo import CryoetNuclearPoreBasketRepository


@pytest.mark.asyncio
async def test_cryoet_nuclear_pore_basket_tomography_repository(db_session):
    repo = CryoetNuclearPoreBasketRepository(db_session)

    study = await repo.create_study(
        name="Study_438_Verification",
        target_specimen="Intact HeLa Cell Nuclear Envelope Vitreous Lamella with 8-Fold NPC Basket",
        analytical_modality="cryoet-npc-basket",
        subtomogram_average_resolution_angstrom=4.15,
        basket_dilation_radius_nm=26.8,
        fg_nucleoporin_confinement_entropy=-14.2,
        transport_receptor_docking_occupancy=0.924,
        confidence_score=0.99,
        status="completed",
        summary_report="Phase 438 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_438_Verification"
    assert study.subtomogram_average_resolution_angstrom == 4.15

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Nuclear_Ring_Tpr_Filament_Conformation",
        profile_category="Primary Step",
        quantitative_value=4.15,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Nuclear_Ring_Tpr_Filament_Conformation"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="subtomogram_average_resolution_angstrom",
        observed_value=4.15,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 4.15

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_438_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
