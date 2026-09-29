"""Tests for Phase 313: Autonomous Spatiotemporal Optogenetic Circuit Simulation & Photostimulation Gene Expression Sculptor Repo."""

import pytest
from database.repositories.optogenetic_spatial_gene_expression_repo import OptogeneticSpatialGeneExpressionRepository


@pytest.mark.asyncio
async def test_optogenetic_spatial_gene_expression_repository(db_session):
    repo = OptogeneticSpatialGeneExpressionRepository(db_session)

    study = await repo.create_study(
        name="Study_313_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="optogenetic-spatial-gene",
        optogenetic_spatial_resolution_microns=12.5,
        transcriptional_induction_dynamic_range_fold=125.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 313 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_313_Verification"
    assert getattr(study, "optogenetic_spatial_resolution_microns") == 12.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Blue_Light_488nm_Cry2_Actuator_Bistable_Morphogen_Grid",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Blue_Light_488nm_Cry2_Actuator_Bistable_Morphogen_Grid"

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
    assert fetched.name == "Study_313_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
