"""API Router for TCR/BCR Clonotype Tracking & Lineage Dynamics."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from database.repositories.tcr_clonotype_tracking_repo import TCRClonotypeRepository
from research.immunology.tcr_clonotype_tracking_engine import TCRClonotypeTrackingEngine

router = APIRouter(prefix="/tcr-clonotype-tracking", tags=["TCR/BCR Clonotype Tracking"])


class ClonotypeInput(BaseModel):
    cdr3_amino_acid: str = Field(..., description="CDR3 amino acid sequence")
    v_gene: str = Field(..., description="V segment gene allele")
    j_gene: str = Field(..., description="J segment gene allele")
    d_gene: Optional[str] = Field(None, description="D segment gene allele")
    clone_frequency: float = Field(..., ge=0.0, le=1.0, description="Relative clonal abundance")
    antigen_specificity: Optional[str] = Field(None, description="Known target epitope or antigen")


class AnalyzeClonotypesRequest(BaseModel):
    study_name: str = Field(..., description="Name of the immune repertoire study")
    sample_source: str = Field("PBMC", description="Biological sample origin (PBMC, TIL, Bone Marrow)")
    repertoire_type: str = Field("TCR_alpha_beta", description="Repertoire receptor category")
    clonotypes: Optional[List[ClonotypeInput]] = Field(None, description="List of sequence clonotypes")


class ClonotypeNodeResponse(BaseModel):
    id: Optional[str] = None
    cdr3_amino_acid: str
    v_gene: str
    j_gene: str
    d_gene: Optional[str] = None
    clone_frequency: float
    expansion_status: str
    antigen_specificity: Optional[str] = None


class DiversityMetricResponse(BaseModel):
    id: Optional[str] = None
    metric_name: str
    metric_value: float
    metric_category: str


class TCRStudyResponse(BaseModel):
    id: str
    study_name: str
    sample_source: str
    repertoire_type: str
    cell_count: int
    shannon_entropy: float
    gini_simpson_index: float
    clonality_score: float
    summary_metrics: Optional[Dict[str, Any]] = None
    clonotypes: List[ClonotypeNodeResponse] = []
    diversity_metrics: List[DiversityMetricResponse] = []
    created_at: str
    updated_at: str


def _serialize(study: Any) -> TCRStudyResponse:
    return TCRStudyResponse(
        id=str(study.id),
        study_name=study.study_name,
        sample_source=study.sample_source,
        repertoire_type=study.repertoire_type,
        cell_count=study.cell_count,
        shannon_entropy=study.shannon_entropy,
        gini_simpson_index=study.gini_simpson_index,
        clonality_score=study.clonality_score,
        summary_metrics=study.summary_metrics or {},
        clonotypes=[
            ClonotypeNodeResponse(
                id=str(c.id),
                cdr3_amino_acid=c.cdr3_amino_acid,
                v_gene=c.v_gene,
                j_gene=c.j_gene,
                d_gene=c.d_gene,
                clone_frequency=c.clone_frequency,
                expansion_status=c.expansion_status,
                antigen_specificity=c.antigen_specificity,
            )
            for c in (study.clonotypes or [])
        ],
        diversity_metrics=[
            DiversityMetricResponse(
                id=str(d.id),
                metric_name=d.metric_name,
                metric_value=d.metric_value,
                metric_category=d.metric_category,
            )
            for d in (study.diversity_metrics or [])
        ],
        created_at=str(study.created_at),
        updated_at=str(study.updated_at),
    )


@router.post("/analyze", response_model=TCRStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_clonotypes(
    payload: AnalyzeClonotypesRequest,
    session: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> TCRStudyResponse:
    engine = TCRClonotypeTrackingEngine()
    clono_dicts = [c.model_dump() for c in payload.clonotypes] if payload.clonotypes else None
    analysis = engine.analyze_clonotype_lineage(
        study_name=payload.study_name,
        sample_source=payload.sample_source,
        repertoire_type=payload.repertoire_type,
        clonotype_data=clono_dicts,
    )

    repo = TCRClonotypeRepository(session)
    study = await repo.create_study(
        study_name=analysis["study_name"],
        sample_source=analysis["sample_source"],
        repertoire_type=analysis["repertoire_type"],
        cell_count=analysis["cell_count"],
        shannon_entropy=analysis["shannon_entropy"],
        gini_simpson_index=analysis["gini_simpson_index"],
        clonality_score=analysis["clonality_score"],
        summary_metrics=analysis["summary_metrics"],
        clonotypes=analysis["clonotypes"],
        diversity_metrics=analysis["diversity_metrics"],
    )
    return _serialize(study)


@router.get("/studies", response_model=List[TCRStudyResponse])
async def list_studies(
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> List[TCRStudyResponse]:
    repo = TCRClonotypeRepository(session)
    studies = await repo.list_studies(limit=limit, offset=offset)
    return [_serialize(s) for s in studies]


@router.get("/studies/{study_id}", response_model=TCRStudyResponse)
async def get_study(
    study_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> TCRStudyResponse:
    repo = TCRClonotypeRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TCR study not found")
    return _serialize(study)


@router.delete("/studies/{study_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_study(
    study_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> None:
    repo = TCRClonotypeRepository(session)
    deleted = await repo.delete_study(study_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TCR study not found")
