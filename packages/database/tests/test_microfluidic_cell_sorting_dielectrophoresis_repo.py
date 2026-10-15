"""Tests for Phase 534: Autonomous High-Throughput 3D Microfluidic Dielectrophoresis (DEP) Circulating Tumor Cell Sorter Repo."""

import pytest
from database.repositories.microfluidic_cell_sorting_dielectrophoresis_repo import MicrofluidicCellSortingDielectrophoresisRepository


@pytest.mark.asyncio
async def test_microfluidic_cell_sorting_dielectrophoresis_repository(db_session):
    repo = MicrofluidicCellSortingDielectrophoresisRepository(db_session)

    study = await repo.create_study(
        name="Study_534_Verification",
        target_specimen="Microfluidic Channel with 3D Quadrupole Electrodes for Label-Free Isolation of Metastatic Breast CTCs",
        analytical_modality="microfluidic-dep-cell-sorting",
        target_cell_recovery_purity_pct=96.8,
        sorting_throughput_cells_per_s=12500.0,
        dielectrophoretic_crossover_frequency_khz=185.0,
        post_sorting_cell_viability_pct=98.2,
        confidence_score=0.994,
        status="completed",
        summary_report="Phase 534 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_534_Verification"
    assert study.target_cell_recovery_purity_pct == 96.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Quadrupole_DEP_Deflection_Streamline_Trajectory",
        profile_category="Primary Step",
        quantitative_value=96.8,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Quadrupole_DEP_Deflection_Streamline_Trajectory"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="target_cell_recovery_purity_pct",
        observed_value=96.8,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 96.8

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_534_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
