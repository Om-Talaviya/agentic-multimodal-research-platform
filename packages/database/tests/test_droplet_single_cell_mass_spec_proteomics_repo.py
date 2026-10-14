"""Tests for Phase 524: Autonomous Picoliter Microfluidic Droplet Single-Cell Mass Spectrometry Proteome Fingerprinter Repo."""

import pytest
from database.repositories.droplet_single_cell_mass_spec_proteomics_repo import DropletSingleCellMassSpecProteomicsRepository


@pytest.mark.asyncio
async def test_droplet_single_cell_mass_spec_proteomics_repository(db_session):
    repo = DropletSingleCellMassSpecProteomicsRepository(db_session)

    study = await repo.create_study(
        name="Study_524_Verification",
        target_specimen="Direct Microfluidic Nano-Electrospray Ionization (nanoESI) Orbitrap MS of Individual Single Glioblastoma Cells",
        analytical_modality="droplet-single-cell-proteomics",
        quantified_proteins_per_single_cell_count=2450.0,
        median_protein_sequence_coverage_pct=28.5,
        sample_loss_reduction_surface_adsorption_pct=94.0,
        single_cell_proteomic_profiling_throughput_cells_per_hr=120.0,
        confidence_score=0.994,
        status="completed",
        summary_report="Phase 524 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_524_Verification"
    assert study.quantified_proteins_per_single_cell_count == 2450.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Nano_ESI_Taylor_Cone_Single_Cell_Peptide_Ionization",
        profile_category="Primary Step",
        quantitative_value=2450.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Nano_ESI_Taylor_Cone_Single_Cell_Peptide_Ionization"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="quantified_proteins_per_single_cell_count",
        observed_value=2450.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 2450.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_524_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
