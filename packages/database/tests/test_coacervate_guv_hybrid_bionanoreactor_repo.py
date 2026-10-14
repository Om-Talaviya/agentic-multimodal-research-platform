"""Tests for Phase 503: Autonomous Synthetic Protocellular Compartment Membraneless Coacervate-GUV Hybrid Bionanoreactor Repo."""

import pytest
from database.repositories.coacervate_guv_hybrid_bionanoreactor_repo import CoacervateGuvHybridBionanoreactorRepository


@pytest.mark.asyncio
async def test_coacervate_guv_hybrid_bionanoreactor_repository(db_session):
    repo = CoacervateGuvHybridBionanoreactorRepository(db_session)

    study = await repo.create_study(
        name="Study_503_Verification",
        target_specimen="Liquid-Liquid Phase Separated Polylysine-ATP Coacervates Encapsulated within POPC/Cholesterol Bilayer GUVs",
        analytical_modality="coacervate-guv-hybrid-reactor",
        enzyme_partition_coefficient_k_partition=38.5,
        internal_substrate_conversion_flux_uM_per_s=12.8,
        membrane_selective_permeation_pore_cutoff_kDa=4.5,
        coacervate_droplet_stability_retention_days=14.0,
        confidence_score=0.993,
        status="completed",
        summary_report="Phase 503 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_503_Verification"
    assert study.enzyme_partition_coefficient_k_partition == 38.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Phase_Separated_Subcompartment_Enzymatic_Cascade",
        profile_category="Primary Step",
        quantitative_value=38.5,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Phase_Separated_Subcompartment_Enzymatic_Cascade"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="enzyme_partition_coefficient_k_partition",
        observed_value=38.5,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 38.5

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_503_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
