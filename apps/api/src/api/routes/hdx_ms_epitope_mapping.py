"""API Router for HDX-MS Conformational Dynamics & Epitope Mapping Engine."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from database.repositories.hdx_ms_epitope_mapping_repo import HDXMSEpitopeRepository
from research.biophysics.hdx_ms_epitope_mapping_engine import HDXMSEpitopeMappingEngine

router = APIRouter(prefix="/hdx-ms-epitope-mapping", tags=["HDX-MS Epitope Mapping"])


class PeptideProfileInput(BaseModel):
    peptide_sequence: str = Field("FNCYFPLQSYGFQPTNGVGYQ", description="Peptic cleavage fragment sequence")
    start_residue: int = Field(486, description="Start residue index")
    end_residue: int = Field(506, description="End residue index")
    deuterium_uptake_apo_pct: float = Field(74.5, description="Apo protein deuterium uptake (%)")
    deuterium_uptake_bound_pct: float = Field(18.2, description="Antibody-bound deuterium uptake (%)")
    delta_deuterium_protection_pct: float = Field(56.3, description="Calculated differential protection ΔD (%)")
    confidence_p_value: float = Field(0.0001, description="Statistical significance p-value")


class RunHDXMappingRequest(BaseModel):
    study_name: str = Field(..., description="Name for the HDX-MS epitope mapping study")
    target_protein_name: str = Field("Spike RBD / Neutralizing mAb", description="Target antigen-antibody complex identifier")
    custom_peptides: Optional[List[PeptideProfileInput]] = None


@router.post("/map-epitope", status_code=status.HTTP_201_CREATED)
async def map_hdx_epitope(
    payload: RunHDXMappingRequest,
    current_user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Execute HDX-MS deuteration uptake differential calculation and conformational epitope mapping."""
    engine = HDXMSEpitopeMappingEngine()
    peptides_data = [p.model_dump() for p in payload.custom_peptides] if payload.custom_peptides else None

    result = engine.map_epitope_protection(
        study_name=payload.study_name,
        target_protein_name=payload.target_protein_name,
        custom_peptides=peptides_data,
    )

    repo = HDXMSEpitopeRepository(session)
    saved_study = await repo.create_study(
        study_name=result["study_name"],
        target_protein_name=result["target_protein_name"],
        peptides_monitored_count=result["peptides_monitored_count"],
        mean_deuteration_protection_pct=result["mean_deuteration_protection_pct"],
        epitope_region_identified=result["epitope_region_identified"],
        summary_metrics=result["summary_metrics"],
        peptides=result["peptides"],
        hotspots=result["hotspots"],
    )

    return {
        "id": str(saved_study.id),
        "status": "success",
        "study_name": saved_study.study_name,
        "target_protein_name": saved_study.target_protein_name,
        "peptides_monitored_count": saved_study.peptides_monitored_count,
        "mean_deuteration_protection_pct": saved_study.mean_deuteration_protection_pct,
        "epitope_region_identified": saved_study.epitope_region_identified,
        "summary_metrics": saved_study.summary_metrics,
        "peptides": [
            {
                "id": str(p.id),
                "peptide_sequence": p.peptide_sequence,
                "start_residue": p.start_residue,
                "end_residue": p.end_residue,
                "deuterium_uptake_apo_pct": p.deuterium_uptake_apo_pct,
                "deuterium_uptake_bound_pct": p.deuterium_uptake_bound_pct,
                "delta_deuterium_protection_pct": p.delta_deuterium_protection_pct,
                "confidence_p_value": p.confidence_p_value,
            }
            for p in saved_study.peptides
        ],
        "hotspots": [
            {
                "id": str(h.id),
                "residue_name": h.residue_name,
                "protection_factor_log2": h.protection_factor_log2,
                "solvent_accessibility_change": h.solvent_accessibility_change,
            }
            for h in saved_study.hotspots
        ],
    }


@router.get("/studies", response_model=List[Dict[str, Any]])
async def list_hdx_studies(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """List recent HDX-MS epitope mapping studies."""
    repo = HDXMSEpitopeRepository(session)
    studies = await repo.list_studies(limit=limit, offset=offset)
    return [
        {
            "id": str(s.id),
            "study_name": s.study_name,
            "target_protein_name": s.target_protein_name,
            "peptides_monitored_count": s.peptides_monitored_count,
            "mean_deuteration_protection_pct": s.mean_deuteration_protection_pct,
            "epitope_region_identified": s.epitope_region_identified,
            "created_at": s.created_at,
        }
        for s in studies
    ]


@router.get("/studies/{study_id}")
async def get_hdx_study(
    study_id: uuid.UUID,
    current_user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieve details for a specific HDX-MS epitope study."""
    repo = HDXMSEpitopeRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"HDX-MS study with ID '{study_id}' not found.",
        )

    return {
        "id": str(study.id),
        "study_name": study.study_name,
        "target_protein_name": study.target_protein_name,
        "peptides_monitored_count": study.peptides_monitored_count,
        "mean_deuteration_protection_pct": study.mean_deuteration_protection_pct,
        "epitope_region_identified": study.epitope_region_identified,
        "summary_metrics": study.summary_metrics,
        "peptides": [
            {
                "id": str(p.id),
                "peptide_sequence": p.peptide_sequence,
                "start_residue": p.start_residue,
                "end_residue": p.end_residue,
                "deuterium_uptake_apo_pct": p.deuterium_uptake_apo_pct,
                "deuterium_uptake_bound_pct": p.deuterium_uptake_bound_pct,
                "delta_deuterium_protection_pct": p.delta_deuterium_protection_pct,
                "confidence_p_value": p.confidence_p_value,
            }
            for p in study.peptides
        ],
        "hotspots": [
            {
                "id": str(h.id),
                "residue_name": h.residue_name,
                "protection_factor_log2": h.protection_factor_log2,
                "solvent_accessibility_change": h.solvent_accessibility_change,
            }
            for h in study.hotspots
        ],
        "created_at": study.created_at,
    }


@router.delete("/studies/{study_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hdx_study(
    study_id: uuid.UUID,
    current_user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> None:
    """Delete an HDX-MS study record by ID."""
    repo = HDXMSEpitopeRepository(session)
    deleted = await repo.delete_study(study_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"HDX-MS study with ID '{study_id}' not found.",
        )
