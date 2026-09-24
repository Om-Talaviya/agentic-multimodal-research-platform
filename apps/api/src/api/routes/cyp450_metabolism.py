"""FastAPI Route for CYP450 Metabolism (Phase 142)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.cyp450_metabolism_repo import CYP450MetabolismRepository
from research.chemistry.cyp450_metabolism_engine import (
    CYP450MetabolismEngine,
    CYP450PredictionRequest,
    CYP450PredictionResult,
)

router = APIRouter(prefix="/cyp450-metabolism", tags=["CYP450 Metabolism"])


@router.post("/predict", response_model=CYP450PredictionResult)
async def predict_cyp450_metabolism(
    payload: CYP450PredictionRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = CYP450MetabolismEngine()
    result = engine.predict(payload)

    repo = CYP450MetabolismRepository(db)
    screen = await repo.create_screen(
        compound_name=result.compound_name,
        smiles=result.smiles,
        intrinsic_clearance_ml_min_kg=result.clint_ml_min_kg,
        hepatic_extraction_ratio=result.hepatic_extraction,
        primary_metabolic_site=result.primary_metabolic_site,
    )

    for iso in result.isoform_predictions:
        await repo.add_isoform_profile(
            screen_id=screen.id,
            isoform_name=iso.isoform,
            inhibition_ic50_um=iso.ic50_um,
            is_inhibitor=iso.is_inhibitor,
            is_substrate=iso.is_substrate,
        )

    for pt in result.clearance_curve:
        await repo.add_clearance_record(
            screen_id=screen.id,
            incubation_time_min=pt.time_min,
            parent_remaining_percent=pt.parent_remaining_pct,
            metabolite_formation_area=100.0 - pt.parent_remaining_pct,
        )

    return result
