"""Tests for Phase 545: Autonomous Microfluidic High-Density Acoustic Droplet Synthetic DNA Digital Archival Writer & Reader Repo."""

import pytest
from database.repositories.microfluidic_acoustic_droplet_dna_storage_repo import MicrofluidicAcousticDropletDnaStorageRepository


@pytest.mark.asyncio
async def test_microfluidic_acoustic_droplet_dna_storage_repository(db_session):
    repo = MicrofluidicAcousticDropletDnaStorageRepository(db_session)

    study = await repo.create_study(
        name="Study_545_Verification",
        target_specimen="Acoustic Ejection Picoliter Well Plate containing Encoded 100-Mbyte Synthetic Oligo Pool with RS ECC",
        analytical_modality="acoustic-droplet-dna-archival",
        dna_archival_data_density_petabytes_per_gram=215.0,
        acoustic_droplet_dispensing_throughput_khz=15.0,
        reed_solomon_error_correction_recovery_pct=100.0,
        per_base_synthesis_accuracy_pct=99.92,
        confidence_score=0.998,
        status="completed",
        summary_report="Phase 545 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_545_Verification"
    assert study.dna_archival_data_density_petabytes_per_gram == 215.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Acoustic_Droplet_Ejection_DNA_Payload_Pulse",
        profile_category="Primary Step",
        quantitative_value=215.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Acoustic_Droplet_Ejection_DNA_Payload_Pulse"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="dna_archival_data_density_petabytes_per_gram",
        observed_value=215.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 215.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_545_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
