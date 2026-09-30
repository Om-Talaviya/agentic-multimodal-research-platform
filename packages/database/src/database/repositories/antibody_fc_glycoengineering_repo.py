"""Repository for Phase 391: Autonomous Therapeutic Monoclonal Antibody Fc Glycoengineering & ADCC Effector Enhancer."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.antibody_fc_glycoengineering import (
    AntibodyFcGlycoengineeringStudy,
    AntibodyFcGlycoengineeringItemProfile,
    AntibodyFcGlycoengineeringMetricTrace,
)


class AntibodyFcGlycoengineeringRepository:
    """Database operations for Autonomous Therapeutic Monoclonal Antibody Fc Glycoengineering & ADCC Effector Enhancer studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "antibody-fc-glycoengineering",
        fc_gamma_receptor_iiia_binding_affinity_increase_fold: float = 52.0,
        antibody_dependent_cellular_cytotoxicity_adcc_lysis_pct: float = 88.5,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> AntibodyFcGlycoengineeringStudy:
        study = AntibodyFcGlycoengineeringStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            fc_gamma_receptor_iiia_binding_affinity_increase_fold=fc_gamma_receptor_iiia_binding_affinity_increase_fold,
            antibody_dependent_cellular_cytotoxicity_adcc_lysis_pct=antibody_dependent_cellular_cytotoxicity_adcc_lysis_pct,
            confidence_score=confidence_score,
            status=status,
            parameters=parameters or {},
            summary_report=summary_report,
        )
        self.session.add(study)
        await self.session.flush()
        await self.session.refresh(study)
        return study

    async def add_item_profile(
        self,
        study_id: UUID,
        item_name: str,
        profile_category: str = "Primary Target",
        quantitative_value: float = 100.0,
        log2_fold_change: float = 1.5,
        significance_score: float = 0.95,
    ) -> AntibodyFcGlycoengineeringItemProfile:
        item = AntibodyFcGlycoengineeringItemProfile(
            study_id=study_id,
            item_name=item_name,
            profile_category=profile_category,
            quantitative_value=quantitative_value,
            log2_fold_change=log2_fold_change,
            significance_score=significance_score,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def add_metric_trace(
        self,
        study_id: UUID,
        metric_dimension: str,
        observed_value: float,
        z_score: float = 2.1,
        p_value: float = 0.001,
    ) -> AntibodyFcGlycoengineeringMetricTrace:
        item = AntibodyFcGlycoengineeringMetricTrace(
            study_id=study_id,
            metric_dimension=metric_dimension,
            observed_value=observed_value,
            z_score=z_score,
            p_value=p_value,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def get_study(self, study_id: UUID) -> Optional[AntibodyFcGlycoengineeringStudy]:
        stmt = select(AntibodyFcGlycoengineeringStudy).where(AntibodyFcGlycoengineeringStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[AntibodyFcGlycoengineeringStudy]:
        stmt = select(AntibodyFcGlycoengineeringStudy).order_by(AntibodyFcGlycoengineeringStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
