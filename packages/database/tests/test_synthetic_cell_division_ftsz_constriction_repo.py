"""Tests for Phase 541: Autonomous Synthetic Protocellular Compartment FtsZ-Min System Dynamic Cleavage Constriction Modeler Repo."""

import pytest
from database.repositories.synthetic_cell_division_ftsz_constriction_repo import SyntheticCellDivisionFtszConstrictionRepository


@pytest.mark.asyncio
async def test_synthetic_cell_division_ftsz_constriction_repository(db_session):
    repo = SyntheticCellDivisionFtszConstrictionRepository(db_session)

    study = await repo.create_study(
        name="Study_541_Verification",
        target_specimen="Cell-Free Microfluidic Giant Unilamellar Vesicle with Reconstituted FtsZ-FtsA and MinCDE Oscillatory Machinery",
        analytical_modality="protocell-ftsz-cleavage-constriction",
        equatorial_constriction_pinching_force_pN=34.0,
        min_protein_pole_to_pole_oscillation_period_s=48.0,
        symmetric_daughter_vesicle_yield_pct=88.5,
        ftsz_treadmilling_velocity_nm_per_s=28.0,
        confidence_score=0.994,
        status="completed",
        summary_report="Phase 541 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_541_Verification"
    assert study.equatorial_constriction_pinching_force_pN == 34.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="FtsZ_Z_Ring_Contractile_Furrow_Complex",
        profile_category="Primary Step",
        quantitative_value=34.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "FtsZ_Z_Ring_Contractile_Furrow_Complex"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="equatorial_constriction_pinching_force_pN",
        observed_value=34.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 34.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_541_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
