"""Tests for Phase 419: Autonomous In-Cell NMR Macromolecular Crowding & Chemical Shift Perturbation Tensor Engine Repo."""

import pytest
from database.repositories.in_cell_nmr_crowding_tensor_repo import InCellNmrCrowdingTensorRepository


@pytest.mark.asyncio
async def test_in_cell_nmr_crowding_tensor_repository(db_session):
    repo = InCellNmrCrowdingTensorRepository(db_session)

    study = await repo.create_study(
        name="Study_419_Verification",
        target_specimen="15N/13C-Enriched Intact E. coli Cytoplasm with Model Protein",
        analytical_modality="in-cell-nmr",
        chemical_shift_perturbation_ppm=0.142,
        rotational_correlation_time_ns=18.4,
        crowding_viscosity_factor=2.85,
        transverse_relaxation_r2_rate=32.1,
        confidence_score=0.982,
        status="completed",
        summary_report="Phase 419 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_419_Verification"
    assert study.chemical_shift_perturbation_ppm == 0.142

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="HSQC_Chemical_Shift_Anisotropy_Tensor",
        profile_category="Primary Step",
        quantitative_value=0.142,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "HSQC_Chemical_Shift_Anisotropy_Tensor"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="chemical_shift_perturbation_ppm",
        observed_value=0.142,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.142

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_419_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
