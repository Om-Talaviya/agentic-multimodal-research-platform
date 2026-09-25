"""FastAPI routes for Phase 181: Rare Disease Deep Phenotyping Studio."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.rare_disease_hpo_phenotyping_repo import RareDiseaseHPOPhenotypingRepository
from research.clinical.rare_disease_hpo_phenotyping_engine import RareDiseaseHPOPhenotypingEngine

router = APIRouter(prefix="/rare-disease-hpo-phenotyping", tags=["Rare Disease Deep Phenotyping"])


class AnalyzePhenotypeRequest(BaseModel):
    name: str = Field(..., example="Patient RD-8841 Deep Phenotyping Analysis")
    patient_cohort_id: str = Field(..., example="PT-RD-8841")
    clinical_narrative: str = Field(..., example="Tall stature, arachnodactyly, aortic root aneurysm, mitral valve prolapse, ectopia lentis")


@router.post("/analyze", status_code=status.HTTP_201_CREATED)
async def analyze_and_persist_phenotype(
    req: AnalyzePhenotypeRequest,
    session: AsyncSession = Depends(get_db_session),
):
    engine = RareDiseaseHPOPhenotypingEngine()
    result = engine.analyze_clinical_phenotype(
        patient_cohort_id=req.patient_cohort_id,
        clinical_narrative=req.clinical_narrative,
    )

    repo = RareDiseaseHPOPhenotypingRepository(session)
    study = await repo.create_study(
        name=req.name,
        patient_cohort_id=result.patient_cohort_id,
        primary_clinical_presentation=result.primary_clinical_presentation,
        extracted_hpo_count=len(result.extracted_hpo_terms),
        top_omim_disease_candidate=result.top_disease_candidate,
        semantic_similarity_resnik_score=result.semantic_similarity_resnik_score,
        diagnostic_prioritization_rank=1,
        causal_gene_symbol=result.causal_gene_symbol,
        inheritance_mode=result.inheritance_mode,
        status="completed",
        parameters={
            "diagnostic_confidence_pct": result.diagnostic_confidence_pct,
        },
        summary_report=result.clinical_recommendation,
    )

    for h in result.extracted_hpo_terms:
        await repo.add_hpo_term(
            study_id=study.id,
            hpo_id=h.hpo_id,
            hpo_label=h.hpo_label,
            information_content_score=h.information_content_score,
            clinical_severity_weight=h.clinical_severity_weight,
            organ_system_category=h.organ_system_category,
        )

    for m in result.ranked_omim_matches:
        await repo.add_omim_match(
            study_id=study.id,
            omim_id=m.omim_id,
            disease_name=m.disease_name,
            causal_genes=m.causal_genes,
            phenomizer_p_value=m.phenomizer_p_value,
            jaccard_similarity_score=m.jaccard_similarity_score,
            matching_terms_count=m.matching_terms_count,
        )

    return {
        "id": str(study.id),
        "name": study.name,
        "patient_cohort_id": study.patient_cohort_id,
        "top_disease_candidate": study.top_omim_disease_candidate,
        "causal_gene_symbol": study.causal_gene_symbol,
        "inheritance_mode": study.inheritance_mode,
        "semantic_similarity_resnik_score": study.semantic_similarity_resnik_score,
        "diagnostic_confidence_pct": result.diagnostic_confidence_pct,
        "clinical_recommendation": result.clinical_recommendation,
        "extracted_hpo_terms": [
            {
                "hpo_id": ht.hpo_id,
                "hpo_label": ht.hpo_label,
                "information_content_score": ht.information_content_score,
                "clinical_severity_weight": ht.clinical_severity_weight,
                "organ_system_category": ht.organ_system_category,
            }
            for ht in result.extracted_hpo_terms
        ],
        "ranked_omim_matches": [
            {
                "omim_id": om.omim_id,
                "disease_name": om.disease_name,
                "causal_genes": om.causal_genes,
                "phenomizer_p_value": om.phenomizer_p_value,
                "jaccard_similarity_score": om.jaccard_similarity_score,
                "matching_terms_count": om.matching_terms_count,
            }
            for om in result.ranked_omim_matches
        ],
    }


@router.get("/studies")
async def list_studies(
    limit: int = Query(default=50, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    repo = RareDiseaseHPOPhenotypingRepository(session)
    studies = await repo.list_studies(limit=limit)
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "patient_cohort_id": s.patient_cohort_id,
            "top_omim_disease_candidate": s.top_omim_disease_candidate,
            "causal_gene_symbol": s.causal_gene_symbol,
            "semantic_similarity_resnik_score": s.semantic_similarity_resnik_score,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in studies
    ]