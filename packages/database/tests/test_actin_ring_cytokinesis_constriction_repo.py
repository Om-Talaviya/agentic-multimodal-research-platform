"""Tests for Phase 477: Autonomous Nanoscale Cytoskeletal Actin Ring Constriction & Cytokinesis Cleavage Furrow Modeler Repo."""

import pytest
from database.repositories.actin_ring_cytokinesis_constriction_repo import ActinRingCytokinesisConstrictionRepository


@pytest.mark.asyncio
async def test_actin_ring_cytokinesis_constriction_repository(db_session):
    repo = ActinRingCytokinesisConstrictionRepository(db_session)

    study = await repo.create_study(
        name="Study_477_Verification",
        target_specimen="Vitrified Dividing S. pombe Protoplast Actomyosin Ring Complex with Myosin-II / Formin Cdc12 Clusters",
        analytical_modality="actin-ring-cytokinesis-constriction",
        contractile_ring_tension_pN=480.0,
        furrow_ingression_velocity_nm_per_s=2.45,
        actin_filament_turnover_rate_s_inv=0.045,
        ring_diameter_constriction_ratio=0.885,
        confidence_score=0.992,
        status="completed",
        summary_report="Phase 477 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_477_Verification"
    assert study.contractile_ring_tension_pN == 480.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Actomyosin_Purse_String_Stress_Constriction",
        profile_category="Primary Step",
        quantitative_value=480.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Actomyosin_Purse_String_Stress_Constriction"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="contractile_ring_tension_pN",
        observed_value=480.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 480.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_477_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
