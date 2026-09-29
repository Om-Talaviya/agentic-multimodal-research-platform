"""Tests for Phase 363: Autonomous Non-Viral Electroporation & Hydrodynamic Gene Delivery Kinetic Transfection Modeler Repo."""

import pytest
from database.repositories.electroporation_gene_delivery_repo import ElectroporationGeneDeliveryRepository


@pytest.mark.asyncio
async def test_electroporation_gene_delivery_repository(db_session):
    repo = ElectroporationGeneDeliveryRepository(db_session)

    study = await repo.create_study(
        name="Study_363_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="electroporation-gene-delivery",
        cell_viability_post_electroporation_pct=88.5,
        crispr_rnp_transfection_efficiency_pct=95.2,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 363 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_363_Verification"
    assert getattr(study, "cell_viability_post_electroporation_pct") == 88.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Primary_Human_T_Cell_Cas9_RNP_Electroporation_Protocol",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Primary_Human_T_Cell_Cas9_RNP_Electroporation_Protocol"

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
    assert fetched.name == "Study_363_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
