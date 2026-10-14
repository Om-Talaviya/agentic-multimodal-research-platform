"""Tests for Phase 473: Autonomous Bio-Piezoelectric Cell Membrane Flexoelectric Curvature Transduction Engine Repo."""

import pytest
from database.repositories.flexoelectric_membrane_curvature_repo import FlexoelectricMembraneCurvatureRepository


@pytest.mark.asyncio
async def test_flexoelectric_membrane_curvature_repository(db_session):
    repo = FlexoelectricMembraneCurvatureRepository(db_session)

    study = await repo.create_study(
        name="Study_473_Verification",
        target_specimen="Asymmetric Phospholipid Bilayer Giant Unilamellar Vesicle with Micropipette Aspiration Curvature",
        analytical_modality="flexoelectric-membrane-curvature",
        flexoelectric_coupling_coefficient_pC_per_m=12.4,
        membrane_curvature_radius_nm=45.0,
        transmembrane_induced_polarization_potential_mV=28.5,
        lipid_dipole_reorientation_energy_kj_mol=3.42,
        confidence_score=0.989,
        status="completed",
        summary_report="Phase 473 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_473_Verification"
    assert study.flexoelectric_coupling_coefficient_pC_per_m == 12.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Curvature_Induced_Lipid_Dipole_Flexoelectric_Polarization",
        profile_category="Primary Step",
        quantitative_value=12.4,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Curvature_Induced_Lipid_Dipole_Flexoelectric_Polarization"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="flexoelectric_coupling_coefficient_pC_per_m",
        observed_value=12.4,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 12.4

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_473_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
