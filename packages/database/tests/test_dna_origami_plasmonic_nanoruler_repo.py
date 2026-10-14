"""Tests for Phase 506: Autonomous DNA Origami Reconfigurable Plasmonic Nanoruler Distance Calibrator Repo."""

import pytest
from database.repositories.dna_origami_plasmonic_nanoruler_repo import DnaOrigamiPlasmonicNanorulerRepository


@pytest.mark.asyncio
async def test_dna_origami_plasmonic_nanoruler_repository(db_session):
    repo = DnaOrigamiPlasmonicNanorulerRepository(db_session)

    study = await repo.create_study(
        name="Study_506_Verification",
        target_specimen="Scaffolded DNA Origami 12-Helix Bundle with Gold Nanoparticle Dimer Heterostructure",
        analytical_modality="dna-origami-plasmonic-nanoruler",
        plasmonic_coupling_resonance_wavelength_nm=648.5,
        interparticle_gap_distance_nm=3.4,
        single_molecule_fluorescence_enhancement_factor=128.0,
        conformational_nanoruler_accuracy_pm=45.0,
        confidence_score=0.995,
        status="completed",
        summary_report="Phase 506 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_506_Verification"
    assert study.plasmonic_coupling_resonance_wavelength_nm == 648.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Nanoparticle_Dimer_Dark_Field_Scattering_Dip",
        profile_category="Primary Step",
        quantitative_value=648.5,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Nanoparticle_Dimer_Dark_Field_Scattering_Dip"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="plasmonic_coupling_resonance_wavelength_nm",
        observed_value=648.5,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 648.5

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_506_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
