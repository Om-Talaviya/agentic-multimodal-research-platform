"""Tests for Phase 201: Therapeutic mRNA LNP Encapsulation & Structure Thermodynamics Engine Repo."""

import pytest
from database.repositories.mrna_lnp_encapsulation_repo import MRNALNPEncapsulationRepository


@pytest.mark.asyncio
async def test_mrna_lnp_encapsulation_repository(db_session):
    repo = MRNALNPEncapsulationRepository(db_session)

    study = await repo.create_study(
        name="Study_201_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="mRNA LNP Encapsulation",
        encapsulation_efficiency_percent=95.8,
        polydispersity_index_pdi=0.082,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 201 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_201_Verification"
    assert getattr(study, "encapsulation_efficiency_percent") == 95.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Ionizable Lipid SM-102 / MC3 Formulation [N:P 6:1]",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Ionizable Lipid SM-102 / MC3 Formulation [N:P 6:1]"

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
    assert fetched.name == "Study_201_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
