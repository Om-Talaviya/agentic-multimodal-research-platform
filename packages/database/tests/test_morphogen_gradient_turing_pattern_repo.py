"""Tests for Phase 456: Autonomous Morphogen Gradient Diffusion-Turing Pattern Self-Organization Simulator Repo."""

import pytest
from database.repositories.morphogen_gradient_turing_pattern_repo import MorphogenGradientTuringPatternRepository


@pytest.mark.asyncio
async def test_morphogen_gradient_turing_pattern_repository(db_session):
    repo = MorphogenGradientTuringPatternRepository(db_session)

    study = await repo.create_study(
        name="Study_456_Verification",
        target_specimen="Synthetic Multicellular Embryoid with Nodal/Lefty Reaction-Diffusion Pattern Formation",
        analytical_modality="morphogen-turing-morphogenesis",
        turing_instability_wavelength_um=48.2,
        nodal_diffusion_coefficient_um2_per_s=12.4,
        pattern_symmetry_breaking_order_parameter=0.895,
        tissue_axis_polarization_ratio=3.85,
        confidence_score=0.988,
        status="completed",
        summary_report="Phase 456 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_456_Verification"
    assert study.turing_instability_wavelength_um == 48.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Nodal_Lefty_Reaction_Diffusion_Frontier",
        profile_category="Primary Step",
        quantitative_value=48.2,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Nodal_Lefty_Reaction_Diffusion_Frontier"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="turing_instability_wavelength_um",
        observed_value=48.2,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 48.2

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_456_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
