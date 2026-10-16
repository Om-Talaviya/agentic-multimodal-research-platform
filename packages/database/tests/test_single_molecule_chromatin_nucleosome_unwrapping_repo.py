"""Tests for Phase 558: Autonomous Single-Molecule Mechanical Force Spectroscopy Chromatin Fiber Nucleosome Unwrapping Modeler Repo."""

import pytest
from database.repositories.single_molecule_chromatin_nucleosome_unwrapping_repo import SingleMoleculeChromatinNucleosomeUnwrappingRepository


@pytest.mark.asyncio
async def test_single_molecule_chromatin_nucleosome_unwrapping_repository(db_session):
    repo = SingleMoleculeChromatinNucleosomeUnwrappingRepository(db_session)

    study = await repo.create_study(
        name="Study_558_Verification",
        target_specimen="Reconstituted 12-Nucleosome Chromatin Array with Widom 601 positioning sequences stretched via Dual-Beam Optical Tweezers",
        analytical_modality="chromatin-force-spectroscopy",
        outer_turn_unwrapping_force_threshold_pn=3.8,
        inner_turn_cooperative_rupture_force_pn=15.2,
        histone_octamer_dissociation_work_kcal_mol=26.4,
        unwrapped_dna_contour_length_release_nm=52.0,
        confidence_score=0.996,
        status="completed",
        summary_report="Phase 558 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_558_Verification"
    assert study.outer_turn_unwrapping_force_threshold_pn == 3.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Two_Stage_Nucleosome_Core_Particle_Unwrapping_Rip",
        profile_category="Primary Step",
        quantitative_value=3.8,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Two_Stage_Nucleosome_Core_Particle_Unwrapping_Rip"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="outer_turn_unwrapping_force_threshold_pn",
        observed_value=3.8,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 3.8

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_558_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
