"""FastAPI routes for Phase 493: Autonomous Quantum Coherent Magnetoreception Cryptochrome Radical Pair Dynamics Simulator."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.cryptochrome_radical_pair_magnetoreception_repo import CryptochromeRadicalPairMagnetoreceptionRepository
from research.orchestration.cryptochrome_radical_pair_magnetoreception_engine import CryptochromeRadicalPairMagnetoreceptionEngine

router = APIRouter(prefix="/cryptochrome-radical-pair-magnetoreception", tags=["cryptochrome-radical-pair-magnetoreception"])


class AnalyzeCryptochromeRadicalPairMagnetoreceptionRequest(BaseModel):
    name: str = Field(..., example="Autonomous Quantum Coherent Magnetoreception Cryptochrome Radical Pair Dynamics Simulator Run")
    target_specimen: str = Field(default="Purified Migratory Avian Cryptochrome-4 (ErCry4) Flavin-Tryptophan Photoreduced Radical Pair")
    analytical_modality: str = Field(default="quantum-radical-pair-magnetoreception")
    input_scale: float = Field(default=1.0, ge=0.1, le=100.0)


class ItemProfileResponse(BaseModel):
    item_name: str
    profile_category: str
    quantitative_value: float
    log2_fold_change: float
    significance_score: float


class MetricTraceResponse(BaseModel):
    metric_dimension: str
    observed_value: float
    z_score: float
    p_value: float


class CryptochromeRadicalPairMagnetoreceptionStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    singlet_triplet_yield_anisotropy_ratio: float
    radical_pair_quantum_coherence_time_us: float
    geomagnetic_field_inclination_sensitivity_nT: float
    spin_state_entanglement_fidelity: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=CryptochromeRadicalPairMagnetoreceptionStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_cryptochrome_radical_pair_magnetoreception(
    req: AnalyzeCryptochromeRadicalPairMagnetoreceptionRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Quantum Coherent Magnetoreception Cryptochrome Radical Pair Dynamics Simulator analysis and persist study."""
    engine = CryptochromeRadicalPairMagnetoreceptionEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = CryptochromeRadicalPairMagnetoreceptionRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        singlet_triplet_yield_anisotropy_ratio=result.singlet_triplet_yield_anisotropy_ratio,
        radical_pair_quantum_coherence_time_us=result.radical_pair_quantum_coherence_time_us,
        geomagnetic_field_inclination_sensitivity_nT=result.geomagnetic_field_inclination_sensitivity_nT,
        spin_state_entanglement_fidelity=result.spin_state_entanglement_fidelity,
        confidence_score=result.confidence_score,
        status="completed",
        summary_report=result.summary_report,
    )

    for item in result.item_profiles:
        await repo.add_item_profile(
            study_id=study.id,
            item_name=item.item_name,
            profile_category=item.profile_category,
            quantitative_value=item.quantitative_value,
            log2_fold_change=item.log2_fold_change,
            significance_score=item.significance_score,
        )

    for trace in result.metric_traces:
        await repo.add_metric_trace(
            study_id=study.id,
            metric_dimension=trace.metric_dimension,
            observed_value=trace.observed_value,
            z_score=trace.z_score,
            p_value=trace.p_value,
        )

    return CryptochromeRadicalPairMagnetoreceptionStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        singlet_triplet_yield_anisotropy_ratio=study.singlet_triplet_yield_anisotropy_ratio,
        radical_pair_quantum_coherence_time_us=study.radical_pair_quantum_coherence_time_us,
        geomagnetic_field_inclination_sensitivity_nT=study.geomagnetic_field_inclination_sensitivity_nT,
        spin_state_entanglement_fidelity=study.spin_state_entanglement_fidelity,
        confidence_score=study.confidence_score,
        status=study.status,
        summary_report=study.summary_report,
        item_profiles=[
            ItemProfileResponse(
                item_name=it.item_name,
                profile_category=it.profile_category,
                quantitative_value=it.quantitative_value,
                log2_fold_change=it.log2_fold_change,
                significance_score=it.significance_score,
            ) for it in result.item_profiles
        ],
        metric_traces=[
            MetricTraceResponse(
                metric_dimension=tr.metric_dimension,
                observed_value=tr.observed_value,
                z_score=tr.z_score,
                p_value=tr.p_value,
            ) for tr in result.metric_traces
        ],
    )


@router.get("/studies", response_model=List[CryptochromeRadicalPairMagnetoreceptionStudyResponse])
async def list_cryptochrome_radical_pair_magnetoreception_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Quantum Coherent Magnetoreception Cryptochrome Radical Pair Dynamics Simulator studies."""
    repo = CryptochromeRadicalPairMagnetoreceptionRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=CryptochromeRadicalPairMagnetoreceptionStudyResponse)
async def get_cryptochrome_radical_pair_magnetoreception_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Quantum Coherent Magnetoreception Cryptochrome Radical Pair Dynamics Simulator study by ID."""
    repo = CryptochromeRadicalPairMagnetoreceptionRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
