"""Tests for Phase 449: Autonomous Microfluidic Droplet Single-Cell Metabolic Metabolomics Isotope Labeling Profiler Repo."""

import pytest
from database.repositories.droplet_single_cell_isotope_metabolomics_repo import DropletSingleCellIsotopeMetabolomicsRepository


@pytest.mark.asyncio
async def test_droplet_single_cell_isotope_metabolomics_repository(db_session):
    repo = DropletSingleCellIsotopeMetabolomicsRepository(db_session)

    study = await repo.create_study(
        name="Study_449_Verification",
        target_specimen="Glucose-13C6 Labeled Glioblastoma Stem-Like Cells in Monodisperse Fluorocarbon Droplets",
        analytical_modality="single-cell-droplet-metabolomics",
        isotopic_enrichment_m3_lactate_ratio=0.765,
        droplet_generation_frequency_khz=4.8,
        glycolytic_flux_attomoles_per_cell_min=38.5,
        mass_accuracy_orbitrap_ppm=0.85,
        confidence_score=0.989,
        status="completed",
        summary_report="Phase 449 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_449_Verification"
    assert study.isotopic_enrichment_m3_lactate_ratio == 0.765

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Glucose_13C_TCA_Cycle_Intermediate_Tracking",
        profile_category="Primary Step",
        quantitative_value=0.765,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Glucose_13C_TCA_Cycle_Intermediate_Tracking"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="isotopic_enrichment_m3_lactate_ratio",
        observed_value=0.765,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.765

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_449_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
