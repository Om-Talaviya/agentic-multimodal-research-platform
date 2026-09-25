"""API Router for siRNA Duplex Thermodynamics & Off-Target Seed Suppressor."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from database.repositories.sirna_thermodynamics_repo import SiRNAThermodynamicsRepository
from research.rnai.sirna_thermodynamics_engine import SiRNAThermodynamicsEngine

router = APIRouter(prefix="/sirna-thermodynamics", tags=["siRNA Thermodynamics"])


class DuplexCandidateInput(BaseModel):
    guide_strand_sequence: str = Field("5'-UUGAGGAACUGUGAAUUUGAG-3'", description="Antisense guide sequence")
    passenger_strand_sequence: str = Field("5'-CAAAUUCACAGUUCCUCAAUU-3'", description="Sense passenger sequence")
    delta_g_5p_kcal_mol: float = Field(-6.8, description="5' terminal free energy (kcal/mol)")
    delta_g_3p_kcal_mol: float = Field(-9.4, description="3' terminal free energy (kcal/mol)")
    seed_region_tm_celsius: float = Field(48.2, description="Seed region melting temperature")
    chemical_mod_pattern: str = Field("2OMe_2F_phosphorothioate", description="Chemical modification motif")


class RunSiRNAEvaluationRequest(BaseModel):
    study_name: str = Field(..., description="Name for the siRNA design and off-target screening study")
    target_mrna_transcript: str = Field("NM_000546.6 (TP53)", description="Target mRNA transcript ID and symbol")
    target_gene: str = Field("TP53", description="Target gene symbol")
    duplex_candidates: Optional[List[DuplexCandidateInput]] = None


@router.post("/evaluate", status_code=status.HTTP_201_CREATED)
async def evaluate_sirna_thermodynamics(
    payload: RunSiRNAEvaluationRequest,
    current_user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Execute duplex thermodynamic asymmetry calculation and off-target seed scoring."""
    engine = SiRNAThermodynamicsEngine()
    candidates_data = [c.model_dump() for c in payload.duplex_candidates] if payload.duplex_candidates else None

    result = engine.evaluate_sirna_thermodynamics(
        study_name=payload.study_name,
        target_mrna_transcript=payload.target_mrna_transcript,
        target_gene=payload.target_gene,
        duplex_candidates=candidates_data,
    )

    repo = SiRNAThermodynamicsRepository(session)
    saved_study = await repo.create_study(
        study_name=result["study_name"],
        target_mrna_transcript=result["target_mrna_transcript"],
        target_gene=result["target_gene"],
        candidates_screened=result["candidates_screened"],
        best_candidate_guide_strand=result["best_candidate_guide_strand"],
        mean_on_target_efficiency=result["mean_on_target_efficiency"],
        summary_metrics=result["summary_metrics"],
        duplexes=result["duplexes"],
        off_targets=result["off_targets"],
    )

    return {
        "id": str(saved_study.id),
        "status": "success",
        "study_name": saved_study.study_name,
        "target_mrna_transcript": saved_study.target_mrna_transcript,
        "target_gene": saved_study.target_gene,
        "candidates_screened": saved_study.candidates_screened,
        "best_candidate_guide_strand": saved_study.best_candidate_guide_strand,
        "mean_on_target_efficiency": saved_study.mean_on_target_efficiency,
        "summary_metrics": saved_study.summary_metrics,
        "duplexes": [
            {
                "id": str(d.id),
                "guide_strand_sequence": d.guide_strand_sequence,
                "passenger_strand_sequence": d.passenger_strand_sequence,
                "delta_g_5p_kcal_mol": d.delta_g_5p_kcal_mol,
                "delta_g_3p_kcal_mol": d.delta_g_3p_kcal_mol,
                "delta_delta_g_asymmetry": d.delta_delta_g_asymmetry,
                "seed_region_tm_celsius": d.seed_region_tm_celsius,
                "risc_loading_preference": d.risc_loading_preference,
                "predicted_knockdown_efficiency": d.predicted_knockdown_efficiency,
                "chemical_mod_pattern": d.chemical_mod_pattern,
            }
            for d in saved_study.duplexes
        ],
        "off_targets": [
            {
                "id": str(o.id),
                "off_target_gene": o.off_target_gene,
                "utr3_seed_match_type": o.utr3_seed_match_type,
                "seed_binding_free_energy": o.seed_binding_free_energy,
                "off_target_silencing_risk": o.off_target_silencing_risk,
            }
            for o in saved_study.off_targets
        ],
    }


@router.get("/studies", response_model=List[Dict[str, Any]])
async def list_sirna_studies(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """List recent siRNA thermodynamic screening studies."""
    repo = SiRNAThermodynamicsRepository(session)
    studies = await repo.list_studies(limit=limit, offset=offset)
    return [
        {
            "id": str(s.id),
            "study_name": s.study_name,
            "target_mrna_transcript": s.target_mrna_transcript,
            "target_gene": s.target_gene,
            "candidates_screened": s.candidates_screened,
            "best_candidate_guide_strand": s.best_candidate_guide_strand,
            "mean_on_target_efficiency": s.mean_on_target_efficiency,
            "created_at": s.created_at,
        }
        for s in studies
    ]


@router.get("/studies/{study_id}")
async def get_sirna_study(
    study_id: uuid.UUID,
    current_user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieve details and candidate metrics for a specific siRNA study."""
    repo = SiRNAThermodynamicsRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"siRNA study with ID '{study_id}' not found.",
        )

    return {
        "id": str(study.id),
        "study_name": study.study_name,
        "target_mrna_transcript": study.target_mrna_transcript,
        "target_gene": study.target_gene,
        "candidates_screened": study.candidates_screened,
        "best_candidate_guide_strand": study.best_candidate_guide_strand,
        "mean_on_target_efficiency": study.mean_on_target_efficiency,
        "summary_metrics": study.summary_metrics,
        "duplexes": [
            {
                "id": str(d.id),
                "guide_strand_sequence": d.guide_strand_sequence,
                "passenger_strand_sequence": d.passenger_strand_sequence,
                "delta_g_5p_kcal_mol": d.delta_g_5p_kcal_mol,
                "delta_g_3p_kcal_mol": d.delta_g_3p_kcal_mol,
                "delta_delta_g_asymmetry": d.delta_delta_g_asymmetry,
                "seed_region_tm_celsius": d.seed_region_tm_celsius,
                "risc_loading_preference": d.risc_loading_preference,
                "predicted_knockdown_efficiency": d.predicted_knockdown_efficiency,
                "chemical_mod_pattern": d.chemical_mod_pattern,
            }
            for d in study.duplexes
        ],
        "off_targets": [
            {
                "id": str(o.id),
                "off_target_gene": o.off_target_gene,
                "utr3_seed_match_type": o.utr3_seed_match_type,
                "seed_binding_free_energy": o.seed_binding_free_energy,
                "off_target_silencing_risk": o.off_target_silencing_risk,
            }
            for o in study.off_targets
        ],
        "created_at": study.created_at,
    }


@router.delete("/studies/{study_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sirna_study(
    study_id: uuid.UUID,
    current_user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> None:
    """Delete an siRNA study record by ID."""
    repo = SiRNAThermodynamicsRepository(session)
    deleted = await repo.delete_study(study_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"siRNA study with ID '{study_id}' not found.",
        )
