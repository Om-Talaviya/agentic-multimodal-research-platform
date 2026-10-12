"""Tests for Phase 421: Autonomous DNA-PAINT Nanometer Super-Resolution Spatial Molecular Counting Engine Repo."""

import pytest
from database.repositories.dna_paint_nanometer_counting_repo import DnaPaintNanometerCountingRepository


@pytest.mark.asyncio
async def test_dna_paint_nanometer_counting_repository(db_session):
    repo = DnaPaintNanometerCountingRepository(db_session)

    study = await repo.create_study(
        name="Study_421_Verification",
        target_specimen="Nuclear Pore Complex Scaffold with Fluorescent Imager Strands",
        analytical_modality="dna-paint-counting",
        spatial_localization_precision_nm=3.15,
        absolute_molecule_count=32.0,
        qpaint_binding_frequency_hz=0.42,
        background_dark_time_ratio=0.978,
        confidence_score=0.993,
        status="completed",
        summary_report="Phase 421 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_421_Verification"
    assert study.spatial_localization_precision_nm == 3.15

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Eightfold_Symmetric_Nup_Scaffold_Cluster",
        profile_category="Primary Step",
        quantitative_value=3.15,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Eightfold_Symmetric_Nup_Scaffold_Cluster"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="spatial_localization_precision_nm",
        observed_value=3.15,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 3.15

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_421_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
