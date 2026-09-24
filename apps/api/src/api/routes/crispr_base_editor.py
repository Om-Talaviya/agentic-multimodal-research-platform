"""
FastAPI Router for Phase 164: CRISPR Base Editor.
"""

import uuid
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from database.repositories.crispr_base_editor_repo import (
    CRISPRBaseEditorRepository,
)
from research.gene_editing.crispr_base_editor_engine import (
    CRISPRBaseEditorEngine,
)

router = APIRouter(prefix="/crispr-base-editor", tags=["CRISPR Base Editing & Bystander Mutation Predictor"])


class BaseEditorPredictionRequest(BaseModel):
    target_gene: str = Field(..., example="PCSK9")
    protospacer_sequence: str = Field(
        ...,
        example="GAACACCCAGAGCCCGGACG",
    )
    editor_type: Optional[str] = Field(default="ABE8e", example="ABE8e")
    pam: Optional[str] = Field(default="NGG", example="NGG")
    workspace_id: Optional[str] = None


@router.post("/predict", status_code=status.HTTP_201_CREATED)
async def predict_base_editing_endpoint(
    req: BaseEditorPredictionRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = CRISPRBaseEditorEngine()
    result = engine.predict_editing_profile(
        target_gene=req.target_gene,
        protospacer_sequence=req.protospacer_sequence,
        editor_type=req.editor_type or "ABE8e",
        pam=req.pam or "NGG",
    )

    repo = CRISPRBaseEditorRepository(db)
    ws_id = uuid.UUID(req.workspace_id) if req.workspace_id else None

    study = await repo.create_study(
        target_gene=result.target_gene,
        editor_type=result.editor_type,
        protospacer_sequence=result.protospacer_sequence,
        pam_sequence=result.pam,
        on_target_conversion_efficiency=result.on_target_efficiency,
        bystander_purity_score=result.bystander_purity_score,
        indel_frequency_percent=result.indel_frequency_percent,
        project_id=ws_id,
    )

    for trans in result.transitions:
        await repo.add_transition(
            study_id=study.id,
            protospacer_position=trans.position,
            initial_base=trans.initial_base,
            target_base=trans.target_base,
            transition_efficiency=trans.efficiency,
            amino_acid_consequence=trans.consequence,
        )

    for bw in result.bystander_windows:
        await repo.add_bystander_window(
            study_id=study.id,
            window_range=bw.window_range,
            bystander_count=bw.bystander_count,
            unintended_mutation_risk_percent=bw.unintended_risk_percent,
            mitigation_strategy=bw.mitigation,
        )

    return {
        "status": "SUCCESS",
        "study_id": str(study.id),
        "target_gene": study.target_gene,
        "editor_type": study.editor_type,
        "on_target_conversion_efficiency": study.on_target_conversion_efficiency,
        "bystander_purity_score": study.bystander_purity_score,
        "result": result.model_dump(),
    }


@router.get("/studies/{study_id}")
async def get_study_endpoint(
    study_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        sid = uuid.UUID(study_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid study UUID")

    repo = CRISPRBaseEditorRepository(db)
    study = await repo.get_study(sid)
    if not study:
        raise HTTPException(status_code=404, detail="CRISPR base editor study not found")

    return {
        "id": str(study.id),
        "target_gene": study.target_gene,
        "editor_type": study.editor_type,
        "protospacer_sequence": study.protospacer_sequence,
        "on_target_conversion_efficiency": study.on_target_conversion_efficiency,
        "transitions_count": len(study.transitions),
        "bystander_windows_count": len(study.bystander_windows),
    }
