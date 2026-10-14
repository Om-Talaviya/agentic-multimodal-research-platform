"""Tests for Phase 504: Autonomous High-Throughput Droplet Microfluidic Ultra-Fast Directed Enzyme Evolution Kinetic Screener Repo."""

import pytest
from database.repositories.droplet_microfluidic_enzyme_evolution_repo import DropletMicrofluidicEnzymeEvolutionRepository


@pytest.mark.asyncio
async def test_droplet_microfluidic_enzyme_evolution_repository(db_session):
    repo = DropletMicrofluidicEnzymeEvolutionRepository(db_session)

    study = await repo.create_study(
        name="Study_504_Verification",
        target_specimen="Picoliter Droplet Emulsion Library of Variant PETase Esterases with Fluorescent Fluorogenic Substrates",
        analytical_modality="droplet-microfluidic-enzyme-screening",
        catalytic_efficiency_improvement_fold=14.8,
        screening_throughput_droplets_per_second=2500.0,
        false_discovery_rate_q_value=0.0015,
        thermostability_delta_tm_celsius=8.5,
        confidence_score=0.996,
        status="completed",
        summary_report="Phase 504 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_504_Verification"
    assert study.catalytic_efficiency_improvement_fold == 14.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Dielectrophoretic_Fluorescence_Activated_Droplet_Sorting",
        profile_category="Primary Step",
        quantitative_value=14.8,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Dielectrophoretic_Fluorescence_Activated_Droplet_Sorting"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="catalytic_efficiency_improvement_fold",
        observed_value=14.8,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 14.8

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_504_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
