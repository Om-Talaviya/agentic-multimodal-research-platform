"""Tests for Phase 537: Autonomous Single-Molecule Magnetic Torque Tweezers (MTT) DNA Supercoiling & Twist Modeler Repo."""

import pytest
from database.repositories.single_molecule_magnetic_torque_tweezer_repo import SingleMoleculeMagneticTorqueTweezerRepository


@pytest.mark.asyncio
async def test_single_molecule_magnetic_torque_tweezer_repository(db_session):
    repo = SingleMoleculeMagneticTorqueTweezerRepository(db_session)

    study = await repo.create_study(
        name="Study_537_Verification",
        target_specimen="Tethered 10-kb Double-Stranded DNA Molecule with Cylindrical Magnetic Bead in Horizontal Torque Field",
        analytical_modality="magnetic-torque-tweezers-supercoiling",
        torsional_persistence_length_nm=84.0,
        buckling_transition_critical_torque_pN_nm=28.5,
        plectoneme_supercoil_conformation_density=0.052,
        dna_twist_stretch_coupling_constant_pN=-95.0,
        confidence_score=0.996,
        status="completed",
        summary_report="Phase 537 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_537_Verification"
    assert study.torsional_persistence_length_nm == 84.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Supercoiled_DNA_Plectoneme_Formation_Burst",
        profile_category="Primary Step",
        quantitative_value=84.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Supercoiled_DNA_Plectoneme_Formation_Burst"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="buckling_transition_critical_torque_pN_nm",
        observed_value=84.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 84.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_537_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
