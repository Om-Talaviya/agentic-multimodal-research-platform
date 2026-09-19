"""API Routes for siRNA & Oligonucleotide Therapeutic Designer (Phase 98)."""

import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.sirna_design_repo import SiRnaDesignRepository
from research.genomics.sirna_engine import SiRnaTherapeuticEngine

router = APIRouter(prefix="/sirna-design", tags=["siRNA & Oligonucleotide Designer"])


class SiRnaDesignRequest(BaseModel):
    target_gene: str = Field(..., example="TTR")
    target_mrna_sequence: str = Field(..., example="AUGGACAGCUACUUUCUUUGCU...")
    custom_seed_exclusion: bool = Field(default=True, example=True)
    workspace_id: Optional[str] = None


@router.post("/optimize", status_code=status.HTTP_201_CREATED)
async def design_sirna_candidate(
    request: SiRnaDesignRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Generate thermodynamic asymmetry-optimized siRNA duplex with chemical modification patterns."""
    engine = SiRnaTherapeuticEngine()
    result = engine.design_sirna(
        target_gene=request.target_gene,
        target_mrna_sequence=request.target_mrna_sequence,
        custom_seed_exclusion=request.custom_seed_exclusion,
    )

    repo = SiRnaDesignRepository(db)
    ws_id = uuid.UUID(request.workspace_id) if request.workspace_id else uuid.uuid4()

    design = await repo.create_design(
        workspace_id=ws_id,
        target_gene=result["target_gene"],
        sense_sequence=result["sense_sequence"],
        antisense_sequence=result["antisense_sequence"],
        knockdown_potency_score=result["knockdown_potency_score"],
        on_target_efficiency_score=result["on_target_efficiency_score"],
        thermodynamic_end_asymmetry=result["thermodynamic_end_asymmetry"],
        tlr_immunogenicity_risk=result["tlr_immunogenicity_risk"],
        off_target_safety_score=result["off_target_safety_score"],
        design_metadata={"summary": result["summary"]},
    )

    for hit in result["off_target_hits"]:
        await repo.add_off_target_hit(
            design_id=design.id,
            off_target_gene=hit["off_target_gene"],
            transcript_id=hit["transcript_id"],
            seed_region_mismatches=hit["seed_region_mismatches"],
            total_mismatches=hit["total_mismatches"],
            predicted_repression_pct=hit["predicted_repression_pct"],
            risk_tier=hit["risk_tier"],
        )

    for mod in result["modifications"]:
        await repo.add_modification(
            design_id=design.id,
            strand=mod["strand"],
            position=mod["position"],
            modification_type=mod["modification_type"],
            nuclease_stability_factor=mod["nuclease_stability_factor"],
        )

    return {
        "status": "SUCCESS",
        "design_id": str(design.id),
        "target_gene": design.target_gene,
        "sense_sequence": design.sense_sequence,
        "antisense_sequence": design.antisense_sequence,
        "knockdown_potency_score": design.knockdown_potency_score,
        "off_target_safety_score": design.off_target_safety_score,
        "off_target_hits": result["off_target_hits"],
        "modifications": result["modifications"],
        "summary": result["summary"],
    }


@router.get("/designs/{design_id}")
async def get_sirna_design(
    design_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Retrieve full siRNA design including off-target hits and chemical modifications."""
    repo = SiRnaDesignRepository(db)
    try:
        did = uuid.UUID(design_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid design UUID format")

    design = await repo.get_design(did)
    if not design:
        raise HTTPException(status_code=404, detail="siRNA design not found")

    return {
        "id": str(design.id),
        "target_gene": design.target_gene,
        "sense_sequence": design.sense_sequence,
        "antisense_sequence": design.antisense_sequence,
        "knockdown_potency_score": design.knockdown_potency_score,
        "off_target_safety_score": design.off_target_safety_score,
        "off_target_hits": [
            {
                "gene": h.off_target_gene,
                "transcript": h.transcript_id,
                "seed_mismatches": h.seed_region_mismatches,
                "risk_tier": h.risk_tier,
            }
            for h in design.off_target_hits
        ],
        "modifications": [
            {
                "strand": m.strand,
                "position": m.position,
                "type": m.modification_type,
            }
            for m in design.modifications
        ],
    }
