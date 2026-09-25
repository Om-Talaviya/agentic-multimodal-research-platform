"""API Router for CADD & In-Silico Variant Pathogenicity Ranker."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from database.repositories.cadd_variant_pathogenicity_repo import CADDVariantRepository
from research.genomics.cadd_variant_pathogenicity_engine import CADDVariantPathogenicityEngine

router = APIRouter(prefix="/cadd-variant-pathogenicity", tags=["CADD Variant Pathogenicity"])


class VariantInput(BaseModel):
    chromosome: str = Field("chr17", description="Chromosome name")
    position: int = Field(..., description="Genomic position (1-based)")
    reference_allele: str = Field(..., description="Reference allele nucleotide")
    alternate_allele: str = Field(..., description="Alternate allele nucleotide")
    hgvs_c: str = Field(..., description="HGVS cDNA notation")


class ScoreVariantsRequest(BaseModel):
    study_name: str = Field(..., description="Name of the variant analysis study")
    genome_build: str = Field("GRCh38", description="Human reference genome build (GRCh38 / GRCh37)")
    target_gene: str = Field("TP53", description="Target gene locus")
    variants: Optional[List[VariantInput]] = Field(None, description="Custom variant list")


class VariantScoreResponse(BaseModel):
    id: Optional[str] = None
    chromosome: str
    position: int
    reference_allele: str
    alternate_allele: str
    hgvs_c: str
    raw_score: float
    phred_score: float
    gerp_score: float
    phylop_score: float
    pathogenicity_verdict: str


class EnsembleScoreResponse(BaseModel):
    id: Optional[str] = None
    algorithm_name: str
    concordance_rate: float
    high_impact_flag: str


class CADDStudyResponse(BaseModel):
    id: str
    study_name: str
    genome_build: str
    target_gene: str
    variant_count: int
    mean_phred_score: float
    deleterious_variant_count: int
    summary_metrics: Optional[Dict[str, Any]] = None
    variants: List[VariantScoreResponse] = []
    ensemble_scores: List[EnsembleScoreResponse] = []
    created_at: str
    updated_at: str


def _serialize(study: Any) -> CADDStudyResponse:
    return CADDStudyResponse(
        id=str(study.id),
        study_name=study.study_name,
        genome_build=study.genome_build,
        target_gene=study.target_gene,
        variant_count=study.variant_count,
        mean_phred_score=study.mean_phred_score,
        deleterious_variant_count=study.deleterious_variant_count,
        summary_metrics=study.summary_metrics or {},
        variants=[
            VariantScoreResponse(
                id=str(v.id),
                chromosome=v.chromosome,
                position=v.position,
                reference_allele=v.reference_allele,
                alternate_allele=v.alternate_allele,
                hgvs_c=v.hgvs_c,
                raw_score=v.raw_score,
                phred_score=v.phred_score,
                gerp_score=v.gerp_score,
                phylop_score=v.phylop_score,
                pathogenicity_verdict=v.pathogenicity_verdict,
            )
            for v in (study.variants or [])
        ],
        ensemble_scores=[
            EnsembleScoreResponse(
                id=str(e.id),
                algorithm_name=e.algorithm_name,
                concordance_rate=e.concordance_rate,
                high_impact_flag=e.high_impact_flag,
            )
            for e in (study.ensemble_scores or [])
        ],
        created_at=str(study.created_at),
        updated_at=str(study.updated_at),
    )


@router.post("/score-variants", response_model=CADDStudyResponse, status_code=status.HTTP_201_CREATED)
async def score_variants(
    payload: ScoreVariantsRequest,
    session: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> CADDStudyResponse:
    engine = CADDVariantPathogenicityEngine()
    var_dicts = [v.model_dump() for v in payload.variants] if payload.variants else None
    result = engine.calculate_cadd_scores(
        study_name=payload.study_name,
        genome_build=payload.genome_build,
        target_gene=payload.target_gene,
        variant_list=var_dicts,
    )

    repo = CADDVariantRepository(session)
    study = await repo.create_study(
        study_name=result["study_name"],
        genome_build=result["genome_build"],
        target_gene=result["target_gene"],
        variant_count=result["variant_count"],
        mean_phred_score=result["mean_phred_score"],
        deleterious_variant_count=result["deleterious_variant_count"],
        summary_metrics=result["summary_metrics"],
        variants=result["variants"],
        ensemble_scores=result["ensemble_scores"],
    )
    return _serialize(study)


@router.get("/studies", response_model=List[CADDStudyResponse])
async def list_studies(
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> List[CADDStudyResponse]:
    repo = CADDVariantRepository(session)
    studies = await repo.list_studies(limit=limit, offset=offset)
    return [_serialize(s) for s in studies]


@router.get("/studies/{study_id}", response_model=CADDStudyResponse)
async def get_study(
    study_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> CADDStudyResponse:
    repo = CADDVariantRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CADD study not found")
    return _serialize(study)


@router.delete("/studies/{study_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_study(
    study_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> None:
    repo = CADDVariantRepository(session)
    deleted = await repo.delete_study(study_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CADD study not found")
