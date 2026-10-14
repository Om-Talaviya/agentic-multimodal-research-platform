"""Tests for Phase 483: Autonomous DNA Origami Molecular Crane Nanomechanical Arm & Rotational Stepper Engine Repo."""

import pytest
from database.repositories.dna_origami_molecular_crane_repo import DnaOrigamiMolecularCraneRepository


@pytest.mark.asyncio
async def test_dna_origami_molecular_crane_repository(db_session):
    repo = DnaOrigamiMolecularCraneRepository(db_session)

    study = await repo.create_study(
        name="Study_483_Verification",
        target_specimen="3D Scaffolded DNA Origami Mechanical Crane with Light-Responsive Azobenzene Rotational Actuator",
        analytical_modality="dna-origami-crane-mechanics",
        crane_arm_rotational_angle_degrees=115.0,
        rotational_step_precision_std_deg=2.1,
        nanomechanical_work_output_kbT=42.0,
        structural_rigidity_persistence_length_nm=850.0,
        confidence_score=0.995,
        status="completed",
        summary_report="Phase 483 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_483_Verification"
    assert study.crane_arm_rotational_angle_degrees == 115.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Azobenzene_Strand_Displacement_Hinge_Pivot",
        profile_category="Primary Step",
        quantitative_value=115.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Azobenzene_Strand_Displacement_Hinge_Pivot"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="crane_arm_rotational_angle_degrees",
        observed_value=115.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 115.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_483_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
