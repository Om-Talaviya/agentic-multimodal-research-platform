"""API Routes for CRISPR Prime & Base Editing Efficiency Predictor (Phase 101)."""

import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.prime_editing_repo import PrimeEditingRepository
from research.genomics.prime_editing_engine import PrimeEditingEngine

router = APIRouter(prefix="/prime-editing", tags=["CRISPR Prime & Base Editing"])


class PrimeEditingRequest(BaseModel):
    target_gene: str = Field(..., example="HBB")
    genomic_locus: str = Field(..., example="chr11:5227002")
    intended_edit: str = Field(..., example="POINT_MUTATION_E6V_CORRECTION")
    editor_architecture: str = Field(default="PEmax_PE3", example="PEmax_PE3")
    workspace_id: Optional[str] = None


@router.post("/design", status_code=status.HTTP_201_CREATED)
async def design_prime_editor(
    request: PrimeEditingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Design pegRNA candidates with optimized PBS/RTT and calculate precision/indel rates."""
    engine = PrimeEditingEngine()
    result = engine.design_prime_editor(
        target_gene=request.target_gene,
        genomic_locus=request.genomic_locus,
        intended_edit=request.intended_edit,
        editor_architecture=request.editor_architecture,
    )

    repo = PrimeEditingRepository(db)
    ws_id = uuid.UUID(request.workspace_id) if request.workspace_id else uuid.uuid4()

    design = await repo.create_design(
        workspace_id=ws_id,
        target_gene=result["target_gene"],
        genomic_locus=result["genomic_locus"],
        intended_edit_type=result["intended_edit_type"],
        editor_architecture=result["editor_architecture"],
        predicted_editing_efficiency_pct=result["predicted_editing_efficiency_pct"],
        purity_score_pct=result["purity_score_pct"],
        indel_frequency_pct=result["indel_frequency_pct"],
        design_metadata={"summary": result["summary"]},
    )

    for cand in result["pegrna_candidates"]:
        await repo.add_pegrna_candidate(
            design_id=design.id,
            spacer_sequence=cand["spacer_sequence"],
            pbs_sequence=cand["pbs_sequence"],
            pbs_length_nt=cand["pbs_length_nt"],
            pbs_tm_celsius=cand["pbs_tm_celsius"],
            rtt_sequence=cand["rtt_sequence"],
            rtt_length_nt=cand["rtt_length_nt"],
            nicking_guide_spacer=cand["nicking_guide_spacer"],
            candidate_rank=cand["candidate_rank"],
        )

    for alt in result["bystander_alerts"]:
        await repo.add_bystander_alert(
            design_id=design.id,
            position_in_window=alt["position_in_window"],
            bystander_base=alt["bystander_base"],
            deamination_risk_score=alt["deamination_risk_score"],
            synonymous_flag=alt["synonymous_flag"],
        )

    return {
        "status": "SUCCESS",
        "design_id": str(design.id),
        "target_gene": design.target_gene,
        "predicted_editing_efficiency_pct": design.predicted_editing_efficiency_pct,
        "purity_score_pct": design.purity_score_pct,
        "indel_frequency_pct": design.indel_frequency_pct,
        "pegrna_candidates": result["pegrna_candidates"],
        "bystander_alerts": result["bystander_alerts"],
        "summary": result["summary"],
    }


@router.get("/designs/{design_id}")
async def get_prime_editing_design(
    design_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Retrieve full prime editing design and pegRNA candidates."""
    repo = PrimeEditingRepository(db)
    try:
        did = uuid.UUID(design_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid design UUID format")

    design = await repo.get_design(did)
    if not design:
        raise HTTPException(status_code=404, detail="Prime editing design not found")

    return {
        "id": str(design.id),
        "target_gene": design.target_gene,
        "genomic_locus": design.genomic_locus,
        "intended_edit_type": design.intended_edit_type,
        "editor_architecture": design.editor_architecture,
        "predicted_editing_efficiency_pct": design.predicted_editing_efficiency_pct,
        "pegrna_candidates": [
            {
                "spacer": c.spacer_sequence,
                "pbs": c.pbs_sequence,
                "pbs_tm": c.pbs_tm_celsius,
                "rtt": c.rtt_sequence,
                "rank": c.candidate_rank,
            }
            for c in design.pegrna_candidates
        ],
        "bystander_alerts": [
            {
                "position": a.position_in_window,
                "base": a.bystander_base,
                "risk": a.deamination_risk_score,
            }
            for a in design.bystander_alerts
        ],
    }
