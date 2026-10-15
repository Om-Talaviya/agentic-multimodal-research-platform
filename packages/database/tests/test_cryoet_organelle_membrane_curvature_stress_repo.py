"""Tests for Phase 536: Autonomous In-Situ Cryo-ET Endoplasmic Reticulum-Mitochondria Membrane Curvature Elastic Stress Profiler Repo."""

import pytest
from database.repositories.cryoet_organelle_membrane_curvature_stress_repo import CryoetOrganelleMembraneCurvatureStressRepository


@pytest.mark.asyncio
async def test_cryoet_organelle_membrane_curvature_stress_repository(db_session):
    repo = CryoetOrganelleMembraneCurvatureStressRepository(db_session)

    study = await repo.create_study(
        name="Study_536_Verification",
        target_specimen="Vitrified Primary Murine Hepatocyte Lamella showing In-Situ MAM (Mitochondria-Associated ER Membrane) Junctions",
        analytical_modality="cryoet-organelle-membrane-stress",
        membrane_bending_modulus_kbT=22.5,
        mam_intermembrane_contact_distance_nm=14.2,
        principal_curvature_radius_nm=18.4,
        lipid_packing_defect_density_per_nm2=0.038,
        confidence_score=0.993,
        status="completed",
        summary_report="Phase 536 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_536_Verification"
    assert study.membrane_bending_modulus_kbT == 22.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="MAM_Tethering_Protein_Complex_Elastic_Deformation",
        profile_category="Primary Step",
        quantitative_value=22.5,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "MAM_Tethering_Protein_Complex_Elastic_Deformation"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="membrane_bending_modulus_kbT",
        observed_value=22.5,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 22.5

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_536_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
