"""Tests for Phase 533: Autonomous DNA Origami Plasmonic Hotspot Nanopore Single-Molecule Optical Tweezers Integrator Repo."""

import pytest
from database.repositories.dna_origami_plasmonic_nanopore_hybrid_repo import DnaOrigamiPlasmonicNanoporeHybridRepository


@pytest.mark.asyncio
async def test_dna_origami_plasmonic_nanopore_hybrid_repository(db_session):
    repo = DnaOrigamiPlasmonicNanoporeHybridRepository(db_session)

    study = await repo.create_study(
        name="Study_533_Verification",
        target_specimen="Hybrid Gold Bowtie Nanoantenna Mounted on 3D DNA Origami Funnel over 5nm Solid-State Nanopore",
        analytical_modality="plasmonic-nanopore-optical-tweezers",
        optical_trapping_stiffness_fN_nm_mW=18.2,
        electromagnetic_hotspot_field_enhancement=450.0,
        single_protein_dwell_extension_factor=64.0,
        ionic_optical_cross_correlation_peak=0.91,
        confidence_score=0.996,
        status="completed",
        summary_report="Phase 533 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_533_Verification"
    assert study.optical_trapping_stiffness_fN_nm_mW == 18.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Bowtie_Antenna_Gap_Single_Molecule_Sensing_Event",
        profile_category="Primary Step",
        quantitative_value=18.2,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Bowtie_Antenna_Gap_Single_Molecule_Sensing_Event"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="electromagnetic_hotspot_field_enhancement",
        observed_value=18.2,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 18.2

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_533_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
