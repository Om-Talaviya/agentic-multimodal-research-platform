"""Tests for Phase 467: Autonomous Living Tissue Origami Programmable 4D Cell-Sheet Self-Folding Mechanics Simulator Repo."""

import pytest
from database.repositories.tissue_origami_cell_sheet_folding_repo import TissueOrigamiCellSheetFoldingRepository


@pytest.mark.asyncio
async def test_tissue_origami_cell_sheet_folding_repository(db_session):
    repo = TissueOrigamiCellSheetFoldingRepository(db_session)

    study = await repo.create_study(
        name="Study_467_Verification",
        target_specimen="Bilayer C2C12 Myoblast / NIH-3T3 Fibroblast Sheet on Thermoresponsive PNIPAM Hydrogel",
        analytical_modality="4d-tissue-origami-folding",
        mean_curvature_folding_radius_mm=1.85,
        interfacial_shear_delamination_strain=0.024,
        programmable_crease_bending_angle_deg=84.5,
        myotube_uniaxial_prestress_kpa=18.2,
        confidence_score=0.993,
        status="completed",
        summary_report="Phase 467 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_467_Verification"
    assert study.mean_curvature_folding_radius_mm == 1.85

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Cell_Sheet_Contraction_4D_Curvature_Fold",
        profile_category="Primary Step",
        quantitative_value=1.85,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Cell_Sheet_Contraction_4D_Curvature_Fold"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="programmable_crease_bending_angle_deg",
        observed_value=1.85,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 1.85

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_467_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
