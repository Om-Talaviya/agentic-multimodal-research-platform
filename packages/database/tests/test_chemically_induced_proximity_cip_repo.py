"""Tests for Phase 298: Autonomous High-Throughput Chemically Induced Proximity (CIP) Multi-Effector Biological Circuit Modeler Repo."""

import pytest
from database.repositories.chemically_induced_proximity_cip_repo import ChemicallyInducedProximityCipRepository


@pytest.mark.asyncio
async def test_chemically_induced_proximity_cip_repository(db_session):
    repo = ChemicallyInducedProximityCipRepository(db_session)

    study = await repo.create_study(
        name="Study_298_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="chemically-induced-proximity-cip",
        cip_transcriptional_activation_fold=180.0,
        ternary_complex_apparent_kd_nM=12.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 298 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_298_Verification"
    assert getattr(study, "cip_transcriptional_activation_fold") == 180.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Rapamycin_Analog_FKBP_FRB_Epigenetic_Switch",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Rapamycin_Analog_FKBP_FRB_Epigenetic_Switch"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="Sensitivity & Recovery Rate",
        observed_value=0.984,
        z_score=2.85,
        p_value=0.00012,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.984

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_298_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
