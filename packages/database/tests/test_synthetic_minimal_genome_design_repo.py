"""Tests for Phase 265: Autonomous Synthetic Minimal Genome Design & Metabolic Essentiality Minimization Engine Repo."""

import pytest
from database.repositories.synthetic_minimal_genome_design_repo import SyntheticMinimalGenomeDesignRepository


@pytest.mark.asyncio
async def test_synthetic_minimal_genome_design_repository(db_session):
    repo = SyntheticMinimalGenomeDesignRepository(db_session)

    study = await repo.create_study(
        name="Study_265_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="synthetic-minimal-genome-design",
        genome_size_reduction_ratio_pct=54.2,
        metabolic_viability_simulation_score=98.2,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 265 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_265_Verification"
    assert getattr(study, "genome_size_reduction_ratio_pct") == 54.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Mycoplasma_JCVI_Syn3_Metabolic_Minimization_Map",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Mycoplasma_JCVI_Syn3_Metabolic_Minimization_Map"

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
    assert fetched.name == "Study_265_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
