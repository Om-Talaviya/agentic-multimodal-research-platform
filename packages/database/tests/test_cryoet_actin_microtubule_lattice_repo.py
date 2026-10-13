"""Tests for Phase 469: Autonomous In-Situ Cryo-ET Cytoskeletal Actin-Microtubule Cross-Linking Structural Lattice Engine Repo."""

import pytest
from database.repositories.cryoet_actin_microtubule_lattice_repo import CryoetActinMicrotubuleLatticeRepository


@pytest.mark.asyncio
async def test_cryoet_actin_microtubule_lattice_repository(db_session):
    repo = CryoetActinMicrotubuleLatticeRepository(db_session)

    study = await repo.create_study(
        name="Study_469_Verification",
        target_specimen="Vitrified Primary Growth Cone Cytoskeleton with Septin/Plectin Cross-Linked Filament Assemblies",
        analytical_modality="cryoet-actin-microtubule-lattice",
        crosslinker_bridge_density_per_um=18.5,
        filament_intersection_angle_distribution_deg=48.2,
        subtomogram_correlation_resolution_angstrom=4.85,
        cytoskeletal_network_rigidity_percolation_tau=0.965,
        confidence_score=0.994,
        status="completed",
        summary_report="Phase 469 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_469_Verification"
    assert study.crosslinker_bridge_density_per_um == 18.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Septin_Plectin_Filament_Intersection_Lattice",
        profile_category="Primary Step",
        quantitative_value=18.5,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Septin_Plectin_Filament_Intersection_Lattice"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="crosslinker_bridge_density_per_um",
        observed_value=18.5,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 18.5

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_469_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
