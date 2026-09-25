"""Repository for Phase 181: Rare Disease Deep Phenotyping & HPO-OMIM Matcher."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.rare_disease_hpo_phenotyping import RDDeepHPOStudy, RDDeepHPOTerm, RDDeepOMIMMatch


class RareDiseaseHPOPhenotypingRepository:
    """Database operations for rare disease deep phenotyping studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        patient_cohort_id: str,
        primary_clinical_presentation: str,
        extracted_hpo_count: int = 6,
        top_omim_disease_candidate: str = "Marfan Syndrome",
        semantic_similarity_resnik_score: float = 0.875,
        diagnostic_prioritization_rank: int = 1,
        causal_gene_symbol: str = "FBN1",
        inheritance_mode: str = "Autosomal dominant",
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> RDDeepHPOStudy:
        study = RDDeepHPOStudy(
            name=name,
            patient_cohort_id=patient_cohort_id,
            primary_clinical_presentation=primary_clinical_presentation,
            extracted_hpo_count=extracted_hpo_count,
            top_omim_disease_candidate=top_omim_disease_candidate,
            semantic_similarity_resnik_score=semantic_similarity_resnik_score,
            diagnostic_prioritization_rank=diagnostic_prioritization_rank,
            causal_gene_symbol=causal_gene_symbol,
            inheritance_mode=inheritance_mode,
            status=status,
            parameters=parameters or {},
            summary_report=summary_report,
        )
        self.session.add(study)
        await self.session.flush()
        await self.session.refresh(study)
        return study

    async def add_hpo_term(
        self,
        study_id: UUID,
        hpo_id: str,
        hpo_label: str,
        information_content_score: float = 6.45,
        clinical_severity_weight: float = 1.0,
        organ_system_category: str = "Skeletal system",
    ) -> RDDeepHPOTerm:
        item = RDDeepHPOTerm(
            study_id=study_id,
            hpo_id=hpo_id,
            hpo_label=hpo_label,
            information_content_score=information_content_score,
            clinical_severity_weight=clinical_severity_weight,
            organ_system_category=organ_system_category,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def add_omim_match(
        self,
        study_id: UUID,
        omim_id: str,
        disease_name: str,
        causal_genes: str,
        phenomizer_p_value: float = 0.00012,
        jaccard_similarity_score: float = 0.78,
        matching_terms_count: int = 5,
    ) -> RDDeepOMIMMatch:
        item = RDDeepOMIMMatch(
            study_id=study_id,
            omim_id=omim_id,
            disease_name=disease_name,
            causal_genes=causal_genes,
            phenomizer_p_value=phenomizer_p_value,
            jaccard_similarity_score=jaccard_similarity_score,
            matching_terms_count=matching_terms_count,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def get_study(self, study_id: UUID) -> Optional[RDDeepHPOStudy]:
        stmt = select(RDDeepHPOStudy).where(RDDeepHPOStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[RDDeepHPOStudy]:
        stmt = select(RDDeepHPOStudy).order_by(RDDeepHPOStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())