"""Tests for Phase 527: Autonomous Membraneless Coacervate RNA Condensation & Ribozyme Catalytic Acceleration Modeler Repo."""

import pytest
from database.repositories.coacervate_nucleic_acid_liquid_condensation_repo import CoacervateNucleicAcidLiquidCondensationRepository


@pytest.mark.asyncio
async def test_coacervate_nucleic_acid_liquid_condensation_repository(db_session):
    repo = CoacervateNucleicAcidLiquidCondensationRepository(db_session)

    study = await repo.create_study(
        name="Study_527_Verification",
        target_specimen="Polycationic Polylysine-Spermidine Complex Coacervate Droplet Encapsulating Hammerhead Ribozymes",
        analytical_modality="coacervate-rna-condensation",
        ribozyme_cleavage_rate_enhancement_fold=48.0,
        partition_coefficient_k_partition=125.0,
        droplet_interfacial_surface_tension_uN_m=0.85,
        critical_coacervation_transition_temp_c=37.2,
        confidence_score=0.994,
        status="completed",
        summary_report="Phase 527 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_527_Verification"
    assert study.ribozyme_cleavage_rate_enhancement_fold == 48.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Dense_Phase_Ribozyme_Substrate_Complex_Cluster",
        profile_category="Primary Step",
        quantitative_value=48.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Dense_Phase_Ribozyme_Substrate_Complex_Cluster"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="ribozyme_cleavage_rate_enhancement_fold",
        observed_value=48.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 48.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_527_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
