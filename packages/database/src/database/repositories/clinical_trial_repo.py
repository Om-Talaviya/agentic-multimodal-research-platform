"""
Repository for Clinical Trial Protocol Optimization & Cohort Stratification.
"""
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from database.models.clinical_trial import (
    DBClinicalTrialProtocol,
    DBEligibilityCriterion,
    DBCohortPatientMatch,
    DBSyntheticControlArm
)

class ClinicalTrialRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_protocol(
        self,
        title: str,
        phase: str,
        target_indication: str,
        investigational_agent: str,
        primary_endpoint: str,
        sample_size_target: int = 120,
        statistical_power: float = 0.85,
        estimated_duration_months: int = 18,
        protocol_summary: Optional[str] = None,
        user_id: Optional[uuid.UUID] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DBClinicalTrialProtocol:
        protocol = DBClinicalTrialProtocol(
            id=uuid.uuid4(),
            user_id=user_id,
            title=title,
            phase=phase,
            target_indication=target_indication,
            investigational_agent=investigational_agent,
            primary_endpoint=primary_endpoint,
            sample_size_target=sample_size_target,
            statistical_power=statistical_power,
            estimated_duration_months=estimated_duration_months,
            protocol_summary=protocol_summary,
            status="OPTIMIZED",
            metadata_=metadata or {}
        )
        self.session.add(protocol)
        await self.session.commit()
        await self.session.refresh(protocol)
        return protocol

    async def get_protocol(self, protocol_id: uuid.UUID) -> Optional[DBClinicalTrialProtocol]:
        query = (
            select(DBClinicalTrialProtocol)
            .options(
                selectinload(DBClinicalTrialProtocol.eligibility_criteria),
                selectinload(DBClinicalTrialProtocol.cohort_matches),
                selectinload(DBClinicalTrialProtocol.synthetic_arms)
            )
            .where(DBClinicalTrialProtocol.id == protocol_id)
        )
        res = await self.session.execute(query)
        return res.scalars().first()

    async def list_protocols(self, limit: int = 50) -> List[DBClinicalTrialProtocol]:
        query = select(DBClinicalTrialProtocol).order_by(DBClinicalTrialProtocol.created_at.desc()).limit(limit)
        res = await self.session.execute(query)
        return list(res.scalars().all())

    async def add_criteria(
        self,
        protocol_id: uuid.UUID,
        criterion_type: str,
        description: str,
        category: str = "CLINICAL",
        structured_rule: Optional[Dict[str, Any]] = None,
        impact_on_enrollment_rate: float = 0.0
    ) -> DBEligibilityCriterion:
        criterion = DBEligibilityCriterion(
            id=uuid.uuid4(),
            protocol_id=protocol_id,
            criterion_type=criterion_type,
            category=category,
            description=description,
            structured_rule=structured_rule or {},
            impact_on_enrollment_rate=impact_on_enrollment_rate
        )
        self.session.add(criterion)
        await self.session.commit()
        await self.session.refresh(criterion)
        return criterion

    async def add_cohort_matches(
        self,
        protocol_id: uuid.UUID,
        matches: List[Dict[str, Any]]
    ) -> List[DBCohortPatientMatch]:
        records = []
        for m in matches:
            record = DBCohortPatientMatch(
                id=uuid.uuid4(),
                protocol_id=protocol_id,
                patient_identifier=m["patient_identifier"],
                phenotype_match_score=m.get("phenotype_match_score", 0.85),
                biomarker_alignment=m.get("biomarker_alignment", "OPTIMAL"),
                eligibility_verdict=m.get("eligibility_verdict", "ELIGIBLE"),
                exclusion_flags=m.get("exclusion_flags", []),
                survival_estimate_months=m.get("survival_estimate_months", 15.0),
                hazard_ratio=m.get("hazard_ratio", 0.65)
            )
            records.append(record)
            self.session.add(record)
        await self.session.commit()
        return records

    async def create_synthetic_control_arm(
        self,
        protocol_id: uuid.UUID,
        rwe_data_source: str,
        baseline_patient_count: int,
        matched_patient_count: int,
        median_os_control: float,
        median_os_interventional: float,
        p_value: float,
        hazard_ratio: float,
        survival_curve: List[Dict[str, Any]]
    ) -> DBSyntheticControlArm:
        arm = DBSyntheticControlArm(
            id=uuid.uuid4(),
            protocol_id=protocol_id,
            rwe_data_source=rwe_data_source,
            baseline_patient_count=baseline_patient_count,
            matched_patient_count=matched_patient_count,
            median_overall_survival_control_months=median_os_control,
            median_overall_survival_interventional_months=median_os_interventional,
            p_value_log_rank=p_value,
            hazard_ratio=hazard_ratio,
            survival_curve_data=survival_curve
        )
        self.session.add(arm)
        await self.session.commit()
        await self.session.refresh(arm)
        return arm
