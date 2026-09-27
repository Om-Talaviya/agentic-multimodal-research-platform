"""Tests for Phase 226: Autonomous In-Situ Cryo-ET Membrane Coat & Clathrin/COP-II Lattice Structural Fitting Engine Repo."""

import pytest
from database.repositories.cryoem_subtomogram_membrane_coat_repo import CryoEMSubtomogramMembraneCoatRepository


@pytest.mark.asyncio
async def test_cryoem_subtomogram_membrane_coat_repository(db_session):
    repo = CryoEMSubtomogramMembraneCoatRepository(db_session)

    study = await repo.create_study(
        name="Study_226_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="cryoem-subtomogram-membrane-coat",
        subtomogram_fsc_resolution_angstrom=3.45,
        lattice_curvature_radius_nm=42.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 226 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_226_Verification"
    assert getattr(study, "subtomogram_fsc_resolution_angstrom") == 3.45

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Sec23_Sec24_COPII_Vesicle_Budding_Lattice",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Sec23_Sec24_COPII_Vesicle_Budding_Lattice"

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
    assert fetched.name == "Study_226_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
