"""Tests for Phase 427: Autonomous CRISPR C-to-G Base Editor (CGBE) & Cas12f Miniature Transposon Editing Forecaster Repo."""

import pytest
from database.repositories.cgbe_cas12f_miniature_editing_repo import CgbeCas12fMiniatureEditingRepository


@pytest.mark.asyncio
async def test_cgbe_cas12f_miniature_editing_repository(db_session):
    repo = CgbeCas12fMiniatureEditingRepository(db_session)

    study = await repo.create_study(
        name="Study_427_Verification",
        target_specimen="Ultra-Compact Cas12f Miniature CGBE Complex in AAV Vector",
        analytical_modality="cgbe-cas12f-editing",
        c_to_g_conversion_purity_percent=88.6,
        on_target_indel_frequency_percent=2.1,
        aav_packaging_size_kb=4.25,
        off_target_cleavage_fraction=0.0035,
        confidence_score=0.987,
        status="completed",
        summary_report="Phase 427 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_427_Verification"
    assert study.c_to_g_conversion_purity_percent == 88.6

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="AAV_All_In_One_Miniature_Cas12f_Cassette",
        profile_category="Primary Step",
        quantitative_value=88.6,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "AAV_All_In_One_Miniature_Cas12f_Cassette"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="c_to_g_conversion_purity_percent",
        observed_value=88.6,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 88.6

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_427_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
