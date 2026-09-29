"""Tests for Phase 312: Autonomous Molecular DNA Digital Data Storage High-Density Synthesis & Nanopore Ionic Translocation Codec Repo."""

import pytest
from database.repositories.nanopore_dna_storage_codec_repo import NanoporeDnaStorageCodecRepository


@pytest.mark.asyncio
async def test_nanopore_dna_storage_codec_repository(db_session):
    repo = NanoporeDnaStorageCodecRepository(db_session)

    study = await repo.create_study(
        name="Study_312_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="nanopore-dna-storage-codec",
        dna_storage_information_density_bits_per_nucleotide=1.96,
        raw_translocation_bit_error_rate_pct=1.25,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 312 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_312_Verification"
    assert getattr(study, "dna_storage_information_density_bits_per_nucleotide") == 1.96

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Petabyte_Scientific_Corpus_Quaternary_Fountain_DNA_Pool",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Petabyte_Scientific_Corpus_Quaternary_Fountain_DNA_Pool"

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
    assert fetched.name == "Study_312_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
