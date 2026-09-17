"""Repository for Clinical Trial Site Selection & Protocol Feasibility."""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from database.models.clinical_site_selection import (
    DBTrialSiteStudy,
    DBCandidateTrialSite,
    DBRecruitmentSimulation,
)


class ClinicalSiteSelectionRepository:
    """Handles async database operations for clinical trial site selection & feasibility."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        study_title: str,
        protocol_code: str,
        indication: str,
        phase: str,
        target_enrollment: int = 100,
        recruitment_duration_months: float = 12.0,
        total_sites: int = 0,
    ) -> DBTrialSiteStudy:
        study = DBTrialSiteStudy(
            study_title=study_title,
            protocol_code=protocol_code,
            indication=indication,
            phase=phase,
            target_enrollment=target_enrollment,
            recruitment_duration_months=recruitment_duration_months,
            total_sites=total_sites,
        )
        self.session.add(study)
        await self.session.commit()
        await self.session.refresh(study)
        return study

    async def get_study(self, study_id: str) -> Optional[DBTrialSiteStudy]:
        stmt = select(DBTrialSiteStudy).where(DBTrialSiteStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[DBTrialSiteStudy]:
        stmt = select(DBTrialSiteStudy).order_by(desc(DBTrialSiteStudy.created_at)).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_sites(
        self,
        study_id: str,
        sites_data: List[Dict[str, Any]],
    ) -> List[DBCandidateTrialSite]:
        created_sites = []
        for s in sites_data:
            site = DBCandidateTrialSite(
                study_id=study_id,
                site_name=s["site_name"],
                country=s["country"],
                city=s["city"],
                principal_investigator=s["principal_investigator"],
                historical_recruitment_rate=s.get("historical_recruitment_rate", 1.0),
                ethics_approval_timeline_days=s.get("ethics_approval_timeline_days", 45),
                patient_pool_density=s.get("patient_pool_density", 1000),
                feasibility_score=s.get("feasibility_score", 0.5),
                risk_tier=s.get("risk_tier", "LOW_RISK"),
                selected_for_trial=s.get("selected_for_trial", True),
                metrics_json=s.get("metrics_json", {}),
            )
            self.session.add(site)
            created_sites.append(site)
        await self.session.commit()
        for site in created_sites:
            await self.session.refresh(site)
        return created_sites

    async def get_sites_by_study(self, study_id: str) -> List[DBCandidateTrialSite]:
        stmt = select(DBCandidateTrialSite).where(DBCandidateTrialSite.study_id == study_id).order_by(desc(DBCandidateTrialSite.feasibility_score))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_simulation(
        self,
        study_id: str,
        simulation_name: str,
        target_timeline_months: float,
        p10_completion_months: float,
        p50_completion_months: float,
        p90_completion_months: float,
        dropout_rate: float = 0.10,
        enrollment_curve_json: Optional[List[Dict[str, Any]]] = None,
        bottleneck_risks_json: Optional[List[Dict[str, Any]]] = None,
    ) -> DBRecruitmentSimulation:
        sim = DBRecruitmentSimulation(
            study_id=study_id,
            simulation_name=simulation_name,
            target_timeline_months=target_timeline_months,
            p10_completion_months=p10_completion_months,
            p50_completion_months=p50_completion_months,
            p90_completion_months=p90_completion_months,
            dropout_rate=dropout_rate,
            enrollment_curve_json=enrollment_curve_json or [],
            bottleneck_risks_json=bottleneck_risks_json or [],
        )
        self.session.add(sim)
        await self.session.commit()
        await self.session.refresh(sim)
        return sim

    async def get_simulations_by_study(self, study_id: str) -> List[DBRecruitmentSimulation]:
        stmt = select(DBRecruitmentSimulation).where(DBRecruitmentSimulation.study_id == study_id).order_by(desc(DBRecruitmentSimulation.created_at))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
