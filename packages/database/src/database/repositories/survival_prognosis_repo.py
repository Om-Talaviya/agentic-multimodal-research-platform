"""
Phase 110: Clinical-Genomic Survival Prognosis & Multi-Omics Stratification Repository.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
import uuid

from database.models.survival_prognosis import (
    DBMultiOmicsPrognosticModel,
    DBSurvivalCohortPatient,
    DBSurvivalStratificationCurve,
)

class SurvivalPrognosisRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_model(
        self,
        model_name: str,
        cancer_cohort: str = "TCGA-LUAD",
        c_index_score: float = 0.82,
        hazard_ratio_high_vs_low: float = 3.45,
        log_rank_p_value: float = 0.0001,
        risk_stratification_method: str = "Cox-Proportional-Hazards",
        features_weights: Optional[Dict[str, Any]] = None,
        project_id: Optional[str] = None,
    ) -> DBMultiOmicsPrognosticModel:
        model = DBMultiOmicsPrognosticModel(
            id=uuid.uuid4(),
            project_id=project_id,
            model_name=model_name,
            cancer_cohort=cancer_cohort,
            c_index_score=c_index_score,
            hazard_ratio_high_vs_low=hazard_ratio_high_vs_low,
            log_rank_p_value=log_rank_p_value,
            risk_stratification_method=risk_stratification_method,
            features_weights=features_weights or {},
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def get_model(self, model_id: uuid.UUID) -> Optional[DBMultiOmicsPrognosticModel]:
        stmt = (
            select(DBMultiOmicsPrognosticModel)
            .options(selectinload(DBMultiOmicsPrognosticModel.patients), selectinload(DBMultiOmicsPrognosticModel.curves))
            .where(DBMultiOmicsPrognosticModel.id == model_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_patient(
        self,
        model_id: uuid.UUID,
        patient_barcode: str,
        overall_survival_months: float,
        vital_status: int,
        risk_group: str,
        risk_score: float,
        biomarker_vector: Optional[Dict[str, Any]] = None,
    ) -> DBSurvivalCohortPatient:
        patient = DBSurvivalCohortPatient(
            id=uuid.uuid4(),
            model_id=model_id,
            patient_barcode=patient_barcode,
            overall_survival_months=overall_survival_months,
            vital_status=vital_status,
            risk_group=risk_group,
            risk_score=risk_score,
            biomarker_vector=biomarker_vector or {},
        )
        self.session.add(patient)
        await self.session.commit()
        await self.session.refresh(patient)
        return patient

    async def add_curve(
        self,
        model_id: uuid.UUID,
        risk_tier: str,
        time_points_months: List[float],
        survival_probability_km: List[float],
        patients_at_risk: List[int],
        median_survival_months: Optional[float] = None,
    ) -> DBSurvivalStratificationCurve:
        curve = DBSurvivalStratificationCurve(
            id=uuid.uuid4(),
            model_id=model_id,
            risk_tier=risk_tier,
            time_points_months=time_points_months,
            survival_probability_km=survival_probability_km,
            patients_at_risk=patients_at_risk,
            median_survival_months=median_survival_months,
        )
        self.session.add(curve)
        await self.session.commit()
        await self.session.refresh(curve)
        return curve

    async def list_patients(self, model_id: uuid.UUID) -> List[DBSurvivalCohortPatient]:
        stmt = select(DBSurvivalCohortPatient).where(DBSurvivalCohortPatient.model_id == model_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_curves(self, model_id: uuid.UUID) -> List[DBSurvivalStratificationCurve]:
        stmt = select(DBSurvivalStratificationCurve).where(DBSurvivalStratificationCurve.model_id == model_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
