"""Tests for Phase 355: Autonomous In Silico T-Cell Exhaustion Epigenetic Rejuvenation & CAR-T Longevity Designer Repo."""

import pytest
from database.repositories.tcell_exhaustion_rejuvenation_repo import TcellExhaustionRejuvenationRepository


@pytest.mark.asyncio
async def test_tcell_exhaustion_rejuvenation_repository(db_session):
    repo = TcellExhaustionRejuvenationRepository(db_session)

    study = await repo.create_study(
        name="Study_355_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="tcell-exhaustion-rejuvenation",
        stem_memory_phenotype_retention_pct=78.5,
        tumor_cytolytic_persistence_half_life_days=68.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 355 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_355_Verification"
    assert getattr(study, "stem_memory_phenotype_retention_pct") == 78.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Stem_Memory_Tscm_Reprogrammed_CD19_CAR_T_Cell_Construct",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Stem_Memory_Tscm_Reprogrammed_CD19_CAR_T_Cell_Construct"

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
    assert fetched.name == "Study_355_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
