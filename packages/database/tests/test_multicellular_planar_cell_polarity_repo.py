"""Tests for Phase 459: Autonomous Synthetic Multicellular Planar Cell Polarity (PCP) Asymmetric Segregation Engine Repo."""

import pytest
from database.repositories.multicellular_planar_cell_polarity_repo import MulticellularPlanarCellPolarityRepository


@pytest.mark.asyncio
async def test_multicellular_planar_cell_polarity_repository(db_session):
    repo = MulticellularPlanarCellPolarityRepository(db_session)

    study = await repo.create_study(
        name="Study_459_Verification",
        target_specimen="Engineered Epithelial Monolayer with Frizzled-6/Vangl2 Core Protein Polarized Ensembles",
        analytical_modality="planar-cell-polarity-segregation",
        asymmetric_crescent_enrichment_ratio=4.25,
        nematic_order_director_coherence=0.885,
        junctional_remodeling_strain_rate_per_hr=0.042,
        global_polarization_vector_magnitude=0.942,
        confidence_score=0.989,
        status="completed",
        summary_report="Phase 459 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_459_Verification"
    assert study.asymmetric_crescent_enrichment_ratio == 4.25

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Frizzled_Vangl2_Opposing_Domain_Segregation",
        profile_category="Primary Step",
        quantitative_value=4.25,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Frizzled_Vangl2_Opposing_Domain_Segregation"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="asymmetric_crescent_enrichment_ratio",
        observed_value=4.25,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 4.25

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_459_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
