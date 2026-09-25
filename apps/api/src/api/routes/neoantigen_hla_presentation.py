"""FastAPI routes for Phase 185: Tumor Neoantigen & HLA Presentation Studio."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.neoantigen_hla_presentation_repo import NeoantigenHLAPresentationRepository
from research.immunology.neoantigen_hla_presentation_engine import NeoantigenHLAPresentationEngine

router = APIRouter(prefix="/neoantigen-hla-presentation", tags=["Tumor Neoantigen & HLA Presentation"])


class SimulateNeoantigenRequest(BaseModel):
    name: str = Field(..., example="Patient MEL-402 Melanoma Neoantigen Screening")
    patient_tumor_id: str = Field(..., example="TUMOR-MEL-402")
    patient_hla_alleles: str = Field(default="HLA-A*02:01, HLA-A*24:02, HLA-B*07:02")
    somatic_mutations_count: int = Field(default=45, ge=1, le=500)


@router.post("/simulate", status_code=status.HTTP_201_CREATED)
async def simulate_and_persist_neoantigen(
    req: SimulateNeoantigenRequest,
    session: AsyncSession = Depends(get_db_session),
):
    engine = NeoantigenHLAPresentationEngine()
    result = engine.simulate_neoantigen_presentation(
        patient_tumor_id=req.patient_tumor_id,
        patient_hla_alleles=req.patient_hla_alleles,
        somatic_mutations_count=req.somatic_mutations_count,
    )

    repo = NeoantigenHLAPresentationRepository(session)
    study = await repo.create_study(
        name=req.name,
        patient_tumor_id=result.patient_tumor_id,
        patient_hla_alleles=result.patient_hla_alleles,
        somatic_mutations_analyzed_count=result.somatic_mutations_analyzed_count,
        high_affinity_neoepitopes_count=result.high_affinity_neoepitopes_count,
        immunogenicity_score_mean=result.immunogenicity_score_mean,
        proteasomal_cleavage_efficiency=result.proteasomal_cleavage_efficiency,
        tap_transport_efficiency=result.tap_transport_efficiency,
        mrna_vaccine_tier1_candidates_count=result.mrna_vaccine_tier1_candidates_count,
        status="completed",
        parameters={
            "immunogenic_fitness_score": result.immunogenic_fitness_score,
        },
        summary_report=result.vaccine_prioritization_recommendation,
    )

    for p in result.peptide_candidates:
        await repo.add_peptide_candidate(
            study_id=study.id,
            gene_symbol=p.gene_symbol,
            mutation_syntax=p.mutation_syntax,
            wildtype_peptide=p.wildtype_peptide,
            mutant_peptide_sequence=p.mutant_peptide_sequence,
            peptide_length=p.peptide_length,
            tcr_recognition_probability=p.tcr_recognition_probability,
        )

    for h in result.hla_predictions:
        await repo.add_hla_prediction(
            study_id=study.id,
            peptide_sequence=h.peptide_sequence,
            hla_allele=h.hla_allele,
            binding_affinity_ic50_nm=h.binding_affinity_ic50_nm,
            presentation_percentile_rank=h.presentation_percentile_rank,
            stability_half_life_hours=h.stability_half_life_hours,
            is_strong_binder=h.is_strong_binder,
        )

    return {
        "id": str(study.id),
        "name": study.name,
        "patient_tumor_id": study.patient_tumor_id,
        "high_affinity_neoepitopes_count": study.high_affinity_neoepitopes_count,
        "mrna_vaccine_tier1_candidates_count": study.mrna_vaccine_tier1_candidates_count,
        "immunogenicity_score_mean": study.immunogenicity_score_mean,
        "immunogenic_fitness_score": result.immunogenic_fitness_score,
        "recommendation": result.vaccine_prioritization_recommendation,
        "peptide_candidates": [
            {
                "gene_symbol": pc.gene_symbol,
                "mutation_syntax": pc.mutation_syntax,
                "wildtype_peptide": pc.wildtype_peptide,
                "mutant_peptide_sequence": pc.mutant_peptide_sequence,
                "tcr_recognition_probability": pc.tcr_recognition_probability,
            }
            for pc in result.peptide_candidates
        ],
        "hla_predictions": [
            {
                "peptide_sequence": hp.peptide_sequence,
                "hla_allele": hp.hla_allele,
                "binding_affinity_ic50_nm": hp.binding_affinity_ic50_nm,
                "presentation_percentile_rank": hp.presentation_percentile_rank,
                "is_strong_binder": hp.is_strong_binder,
            }
            for hp in result.hla_predictions
        ],
    }


@router.get("/studies")
async def list_studies(
    limit: int = Query(default=50, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    repo = NeoantigenHLAPresentationRepository(session)
    studies = await repo.list_studies(limit=limit)
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "patient_tumor_id": s.patient_tumor_id,
            "high_affinity_neoepitopes_count": s.high_affinity_neoepitopes_count,
            "mrna_vaccine_tier1_candidates_count": s.mrna_vaccine_tier1_candidates_count,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in studies
    ]