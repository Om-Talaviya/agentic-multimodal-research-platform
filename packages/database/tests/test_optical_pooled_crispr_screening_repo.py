"""Tests for Phase 377: Autonomous High-Throughput Optical Pooled CRISPR Screening Phenotypic Image Decoder Repo."""

import pytest
from database.repositories.optical_pooled_crispr_screening_repo import OpticalPooledCrisprScreeningRepository


@pytest.mark.asyncio
async def test_optical_pooled_crispr_screening_repository(db_session):
    repo = OpticalPooledCrisprScreeningRepository(db_session)

    study = await repo.create_study(
        name="Study_377_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="optical-pooled-crispr-screening",
        optical_barcode_calling_accuracy_pct=99.2,
        single_cell_phenotype_classification_f1_score=0.945,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 377 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_377_Verification"
    assert getattr(study, "optical_barcode_calling_accuracy_pct") == 99.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Genome_Wide_DNA_Damage_Response_Optical_Screen_Plate",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Genome_Wide_DNA_Damage_Response_Optical_Screen_Plate"

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
    assert fetched.name == "Study_377_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
