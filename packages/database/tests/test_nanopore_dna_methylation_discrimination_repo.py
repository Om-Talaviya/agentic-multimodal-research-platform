"""Tests for Phase 478: Autonomous Solid-State Nanopore DNA Methylation Direct Ionic Current Discrimination Engine Repo."""

import pytest
from database.repositories.nanopore_dna_methylation_discrimination_repo import NanoporeDnaMethylationDiscriminationRepository


@pytest.mark.asyncio
async def test_nanopore_dna_methylation_discrimination_repository(db_session):
    repo = NanoporeDnaMethylationDiscriminationRepository(db_session)

    study = await repo.create_study(
        name="Study_478_Verification",
        target_specimen="Sub-2nm Si3N4 Nanopore Translocating Native Synthetic 5mC / 5hmC Epigenetic DNA Duplexes",
        analytical_modality="nanopore-methylation-discrimination",
        fractional_current_blockade_ratio=0.842,
        epigenetic_base_dwell_time_us=18.5,
        five_mc_vs_unmethylated_snr_db=14.8,
        single_base_resolution_confidence=0.988,
        confidence_score=0.991,
        status="completed",
        summary_report="Phase 478 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_478_Verification"
    assert study.fractional_current_blockade_ratio == 0.842

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="5mC_Steric_Hindrance_Ionic_Drop_Profile",
        profile_category="Primary Step",
        quantitative_value=0.842,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "5mC_Steric_Hindrance_Ionic_Drop_Profile"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="fractional_current_blockade_ratio",
        observed_value=0.842,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.842

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_478_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
