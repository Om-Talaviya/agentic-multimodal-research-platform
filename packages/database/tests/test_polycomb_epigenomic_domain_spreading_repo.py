"""Tests for Phase 446: Autonomous Spatial Epigenomic Histone H3K27me3 Polycomb Repressive Domain Spreading Modeler Repo."""

import pytest
from database.repositories.polycomb_epigenomic_domain_spreading_repo import PolycombEpigenomicDomainRepository


@pytest.mark.asyncio
async def test_polycomb_epigenomic_domain_spreading_repository(db_session):
    repo = PolycombEpigenomicDomainRepository(db_session)

    study = await repo.create_study(
        name="Study_446_Verification",
        target_specimen="Pluripotent Embryonic Stem Cells Differentiation Locus Chromatin Super-Domain",
        analytical_modality="polycomb-epigenomic-spreading",
        polycomb_spreading_velocity_bp_per_hr=1450.0,
        prc2_nucleosome_occupancy_ratio=0.895,
        chromatin_compaction_density_nm=28.4,
        transcriptional_repression_half_life_days=6.8,
        confidence_score=0.988,
        status="completed",
        summary_report="Phase 446 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_446_Verification"
    assert study.polycomb_spreading_velocity_bp_per_hr == 1450.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="H3K27me3_Catalytic_Read_Write_Domain_Boundary",
        profile_category="Primary Step",
        quantitative_value=1450.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "H3K27me3_Catalytic_Read_Write_Domain_Boundary"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="polycomb_spreading_velocity_bp_per_hr",
        observed_value=1450.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 1450.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_446_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
