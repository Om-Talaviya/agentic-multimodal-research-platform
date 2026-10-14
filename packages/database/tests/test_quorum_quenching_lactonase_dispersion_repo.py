"""Tests for Phase 485: Autonomous Bacterial Quorum Quenching Enzymatic Lactonase Biofilm Dispersion Forecaster Repo."""

import pytest
from database.repositories.quorum_quenching_lactonase_dispersion_repo import QuorumQuenchingLactonaseDispersionRepository


@pytest.mark.asyncio
async def test_quorum_quenching_lactonase_dispersion_repository(db_session):
    repo = QuorumQuenchingLactonaseDispersionRepository(db_session)

    study = await repo.create_study(
        name="Study_485_Verification",
        target_specimen="Pseudomonas aeruginosa PAO1 Mature Biofilm with Immobilized Phosphotriesterase-Like Lactonase (PLL)",
        analytical_modality="quorum-quenching-lactonase",
        ahl_hydrolysis_kcat_over_km_M_inv_s_inv=280000.0,
        biofilm_extracellular_matrix_reduction_pct=78.5,
        quorum_regulated_pyocyanin_suppression_pct=92.4,
        antibiotic_potency_synergy_fold_increase=6.4,
        confidence_score=0.988,
        status="completed",
        summary_report="Phase 485 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_485_Verification"
    assert study.ahl_hydrolysis_kcat_over_km_M_inv_s_inv == 280000.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Acyl_Homoserine_Lactone_Lactonolysis_Depletion",
        profile_category="Primary Step",
        quantitative_value=280000.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Acyl_Homoserine_Lactone_Lactonolysis_Depletion"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="biofilm_extracellular_matrix_reduction_pct",
        observed_value=280000.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 280000.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_485_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
