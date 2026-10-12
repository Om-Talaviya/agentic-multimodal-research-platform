"""Tests for Phase 428: Autonomous In-Situ Liquid-Cell Transmission Electron Microscopy (LC-TEM) Nanoparticle Nucleation Simulator Repo."""

import pytest
from database.repositories.liquid_cell_tem_nucleation_repo import LiquidCellTemNucleationRepository


@pytest.mark.asyncio
async def test_liquid_cell_tem_nucleation_repository(db_session):
    repo = LiquidCellTemNucleationRepository(db_session)

    study = await repo.create_study(
        name="Study_428_Verification",
        target_specimen="Silicon Nitride Liquid Cell with Gold Nanocrystal Growth Solution",
        analytical_modality="liquid-cell-tem",
        nucleation_rate_particles_per_s_um2=14.2,
        critical_nucleus_radius_nm=1.45,
        non_classical_attachment_frequency=0.785,
        electron_beam_dose_rate_e_per_ang2_s=8.5,
        confidence_score=0.984,
        status="completed",
        summary_report="Phase 428 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_428_Verification"
    assert study.nucleation_rate_particles_per_s_um2 == 14.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Prenucleation_Cluster_Coalescence_Pathway",
        profile_category="Primary Step",
        quantitative_value=14.2,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Prenucleation_Cluster_Coalescence_Pathway"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="nucleation_rate_particles_per_s_um2",
        observed_value=14.2,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 14.2

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_428_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
