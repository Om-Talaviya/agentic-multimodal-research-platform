"""API Router for Epigenetic DNA Methylation Biological Age Clocks."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from database.repositories.dna_methylation_clock_repo import DNAMethylationClockRepository
from research.epigenetics.dna_methylation_clock_engine import DNAMethylationClockEngine

router = APIRouter(prefix="/dna-methylation-clock", tags=["Epigenetic DNA Methylation Clock"])


class CpGProbeInput(BaseModel):
    cpg_probe_id: str = Field(..., description="Illumina Infinium CpG identifier (e.g., cg02228185)")
    target_gene: str = Field(..., description="Annotated target gene symbol")
    chromosome: str = Field("chr1", description="Chromosome name")
    genomic_coordinate: int = Field(..., description="Base pair position")
    beta_value: float = Field(..., ge=0.0, le=1.0, description="Methylation beta ratio [0,1]")
    clock_weight: float = Field(..., description="Trained regression coefficient")


class EstimateAgeRequest(BaseModel):
    study_name: str = Field(..., description="Epigenetic study name")
    sample_identifier: str = Field("DONOR-EPIGEN-01", description="Donor/Patient ID")
    tissue_type: str = Field("whole_blood", description="Tissue source")
    chronological_age: float = Field(..., ge=0.0, le=130.0, description="Chronological age in years")
    cpg_probes: Optional[List[CpGProbeInput]] = Field(None, description="Custom CpG beta array values")


class CpGMarkerResponse(BaseModel):
    id: Optional[str] = None
    cpg_probe_id: str
    target_gene: str
    chromosome: str
    genomic_coordinate: int
    beta_value: float
    clock_weight: float


class AgeMetricResponse(BaseModel):
    id: Optional[str] = None
    clock_algorithm: str
    predicted_epigenetic_age: float
    acceleration_residual: float
    mortality_hazard_ratio: float


class MethylationStudyResponse(BaseModel):
    id: str
    study_name: str
    sample_identifier: str
    tissue_type: str
    chronological_age: float
    horvath_predicted_age: float
    hannum_predicted_age: float
    phenoage_predicted_age: float
    grimage_mortality_risk_score: float
    age_acceleration_delta: float
    summary_metrics: Optional[Dict[str, Any]] = None
    cpg_markers: List[CpGMarkerResponse] = []
    age_metrics: List[AgeMetricResponse] = []
    created_at: str
    updated_at: str


def _serialize(study: Any) -> MethylationStudyResponse:
    return MethylationStudyResponse(
        id=str(study.id),
        study_name=study.study_name,
        sample_identifier=study.sample_identifier,
        tissue_type=study.tissue_type,
        chronological_age=study.chronological_age,
        horvath_predicted_age=study.horvath_predicted_age,
        hannum_predicted_age=study.hannum_predicted_age,
        phenoage_predicted_age=study.phenoage_predicted_age,
        grimage_mortality_risk_score=study.grimage_mortality_risk_score,
        age_acceleration_delta=study.age_acceleration_delta,
        summary_metrics=study.summary_metrics or {},
        cpg_markers=[
            CpGMarkerResponse(
                id=str(m.id),
                cpg_probe_id=m.cpg_probe_id,
                target_gene=m.target_gene,
                chromosome=m.chromosome,
                genomic_coordinate=m.genomic_coordinate,
                beta_value=m.beta_value,
                clock_weight=m.clock_weight,
            )
            for m in (study.cpg_markers or [])
        ],
        age_metrics=[
            AgeMetricResponse(
                id=str(a.id),
                clock_algorithm=a.clock_algorithm,
                predicted_epigenetic_age=a.predicted_epigenetic_age,
                acceleration_residual=a.acceleration_residual,
                mortality_hazard_ratio=a.mortality_hazard_ratio,
            )
            for a in (study.age_metrics or [])
        ],
        created_at=str(study.created_at),
        updated_at=str(study.updated_at),
    )


@router.post("/estimate-age", response_model=MethylationStudyResponse, status_code=status.HTTP_201_CREATED)
async def estimate_age(
    payload: EstimateAgeRequest,
    session: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> MethylationStudyResponse:
    engine = DNAMethylationClockEngine()
    probes_dicts = [p.model_dump() for p in payload.cpg_probes] if payload.cpg_probes else None
    result = engine.compute_epigenetic_age(
        study_name=payload.study_name,
        sample_identifier=payload.sample_identifier,
        tissue_type=payload.tissue_type,
        chronological_age=payload.chronological_age,
        cpg_probes=probes_dicts,
    )

    repo = DNAMethylationClockRepository(session)
    study = await repo.create_study(
        study_name=result["study_name"],
        sample_identifier=result["sample_identifier"],
        tissue_type=result["tissue_type"],
        chronological_age=result["chronological_age"],
        horvath_predicted_age=result["horvath_predicted_age"],
        hannum_predicted_age=result["hannum_predicted_age"],
        phenoage_predicted_age=result["phenoage_predicted_age"],
        grimage_mortality_risk_score=result["grimage_mortality_risk_score"],
        age_acceleration_delta=result["age_acceleration_delta"],
        summary_metrics=result["summary_metrics"],
        cpg_markers=result["cpg_markers"],
        age_metrics=result["age_metrics"],
    )
    return _serialize(study)


@router.get("/studies", response_model=List[MethylationStudyResponse])
async def list_studies(
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> List[MethylationStudyResponse]:
    repo = DNAMethylationClockRepository(session)
    studies = await repo.list_studies(limit=limit, offset=offset)
    return [_serialize(s) for s in studies]


@router.get("/studies/{study_id}", response_model=MethylationStudyResponse)
async def get_study(
    study_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> MethylationStudyResponse:
    repo = DNAMethylationClockRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Methylation study not found")
    return _serialize(study)


@router.delete("/studies/{study_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_study(
    study_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> None:
    repo = DNAMethylationClockRepository(session)
    deleted = await repo.delete_study(study_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Methylation study not found")
