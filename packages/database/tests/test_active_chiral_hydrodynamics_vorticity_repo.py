"""Tests for Phase 549: Autonomous Non-Equilibrium Active Chiral Hydrodynamics Swarming Vorticity Modeler Repo."""

import pytest
from database.repositories.active_chiral_hydrodynamics_vorticity_repo import ActiveChiralHydrodynamicsVorticityRepository


@pytest.mark.asyncio
async def test_active_chiral_hydrodynamics_vorticity_repository(db_session):
    repo = ActiveChiralHydrodynamicsVorticityRepository(db_session)

    study = await repo.create_study(
        name="Study_549_Verification",
        target_specimen="Chiral Rotating Flagellated Micro-Swarm Escherichia coli in Confined Annular Microfluidic Cavities",
        analytical_modality="active-chiral-hydrodynamics",
        swarming_vorticity_enstrophy_density_s2=145.2,
        chiral_odd_viscosity_coefficient_pa_s=0.082,
        collective_topological_circulation_rate_rad_s=18.4,
        microfluidic_boundary_shear_stress_pa=0.36,
        confidence_score=0.994,
        status="completed",
        summary_report="Phase 549 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_549_Verification"
    assert study.swarming_vorticity_enstrophy_density_s2 == 145.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Odd_Viscosity_Mesoscale_Vortex_Lattice_Core",
        profile_category="Primary Step",
        quantitative_value=145.2,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Odd_Viscosity_Mesoscale_Vortex_Lattice_Core"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="swarming_vorticity_enstrophy_density_s2",
        observed_value=145.2,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 145.2

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_549_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
