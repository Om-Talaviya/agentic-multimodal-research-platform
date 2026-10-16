"""Tests for Phase 551: Autonomous Engineered Magnetotactic Bacterial Magnetosome Nanowire Steering & Drug Cargo Transport Simulator Repo."""

import pytest
from database.repositories.magnetotactic_bacterial_magnetosome_transport_repo import MagnetotacticBacterialMagnetosomeTransportRepository


@pytest.mark.asyncio
async def test_magnetotactic_bacterial_magnetosome_transport_repository(db_session):
    repo = MagnetotacticBacterialMagnetosomeTransportRepository(db_session)

    study = await repo.create_study(
        name="Study_551_Verification",
        target_specimen="Engineered Magnetospirillum magneticum AMB-1 expressing Doxorubicin-Loaded Membrane Nanovesicles in Microfluidic Vascular Capillaries",
        analytical_modality="bacterial-magnetosome-transport",
        magnetic_steering_velocity_um_s=48.5,
        magnetosome_chain_magnetic_moment_femu=12.5,
        tumor_microvascular_extravasation_rate_pct=34.2,
        nanocarrier_drug_payload_delivery_ng_ml=82.0,
        confidence_score=0.995,
        status="completed",
        summary_report="Phase 551 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_551_Verification"
    assert study.magnetic_steering_velocity_um_s == 48.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Vascular_Shear_Resistant_Magnetosome_Nanowire_Alignment",
        profile_category="Primary Step",
        quantitative_value=48.5,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Vascular_Shear_Resistant_Magnetosome_Nanowire_Alignment"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="magnetic_steering_velocity_um_s",
        observed_value=48.5,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 48.5

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_551_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
