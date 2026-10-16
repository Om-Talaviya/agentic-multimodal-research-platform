"""Tests for Phase 550: Autonomous High-Throughput Droplet-Based Single-Cell Epigenomic DNA Hydroxymethylation (5hmC) Profiler Repo."""

import pytest
from database.repositories.single_cell_5hmc_droplet_profiler_repo import SingleCell5HmcDropletProfilerRepository


@pytest.mark.asyncio
async def test_single_cell_5hmc_droplet_profiler_repository(db_session):
    repo = SingleCell5HmcDropletProfilerRepository(db_session)

    study = await repo.create_study(
        name="Study_550_Verification",
        target_specimen="Single-Cell Microfluidic Barcoded Mouse Hippocampal Neurons subjected to T4 beta-Glucosyltransferase Glucosylation",
        analytical_modality="droplet-epigenomic-5hmc",
        hydroxyl_methylated_cytosine_enrichment_fold=24.6,
        single_cell_epigenomic_capture_efficiency_pct=91.5,
        brain_active_enhancer_5hmc_density_per_kb=4.12,
        enzymatic_glucosylation_stoichiometry_pct=97.8,
        confidence_score=0.996,
        status="completed",
        summary_report="Phase 550 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_550_Verification"
    assert study.hydroxyl_methylated_cytosine_enrichment_fold == 24.6

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Synaptic_Plasticity_Enhancer_5hmC_Epigenetic_Peak",
        profile_category="Primary Step",
        quantitative_value=24.6,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Synaptic_Plasticity_Enhancer_5hmC_Epigenetic_Peak"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="hydroxyl_methylated_cytosine_enrichment_fold",
        observed_value=24.6,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 24.6

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_550_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
