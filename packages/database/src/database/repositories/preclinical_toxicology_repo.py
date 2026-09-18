"""Repository for Preclinical Toxicogenomics & ADMET Safety Risk Analysis."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from database.models.preclinical_toxicology import (
    DBPreclinicalToxStudy,
    DBToxicogenomicEndpoint,
    DBStructuralToxAlert,
)


class PreclinicalToxicologyRepository:
    """Repository handling CRUD operations for preclinical toxicogenomics and ADMET risk assessments."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        workspace_id: UUID,
        compound_name: str,
        smiles_string: str,
        therapeutic_safety_index: float = 75.0,
        overall_safety_tier: str = "FAVORABLE",
        caco2_permeability_cm_s: float = 1.5e-5,
        plasma_protein_binding_pct: float = 88.5,
        study_metadata: Optional[Dict[str, Any]] = None,
    ) -> DBPreclinicalToxStudy:
        study = DBPreclinicalToxStudy(
            workspace_id=workspace_id,
            compound_name=compound_name,
            smiles_string=smiles_string,
            therapeutic_safety_index=therapeutic_safety_index,
            overall_safety_tier=overall_safety_tier,
            caco2_permeability_cm_s=caco2_permeability_cm_s,
            plasma_protein_binding_pct=plasma_protein_binding_pct,
            study_metadata=study_metadata or {},
        )
        self.session.add(study)
        await self.session.commit()
        await self.session.refresh(study)
        return study

    async def get_study(self, study_id: UUID) -> Optional[DBPreclinicalToxStudy]:
        query = (
            select(DBPreclinicalToxStudy)
            .where(DBPreclinicalToxStudy.id == study_id)
            .options(
                selectinload(DBPreclinicalToxStudy.endpoints),
                selectinload(DBPreclinicalToxStudy.tox_alerts),
            )
        )
        res = await self.session.execute(query)
        return res.scalars().first()

    async def list_studies(self, workspace_id: UUID, limit: int = 50, offset: int = 0) -> List[DBPreclinicalToxStudy]:
        query = (
            select(DBPreclinicalToxStudy)
            .where(DBPreclinicalToxStudy.workspace_id == workspace_id)
            .order_by(desc(DBPreclinicalToxStudy.created_at))
            .limit(limit)
            .offset(offset)
        )
        res = await self.session.execute(query)
        return list(res.scalars().all())

    async def add_endpoint(
        self,
        study_id: UUID,
        endpoint_name: str,
        endpoint_category: str,
        probability_risk: float,
        measured_or_predicted_value: float,
        unit: str = "uM",
        risk_classification: str = "LOW",
        confidence_score: float = 0.90,
    ) -> DBToxicogenomicEndpoint:
        ep = DBToxicogenomicEndpoint(
            study_id=study_id,
            endpoint_name=endpoint_name,
            endpoint_category=endpoint_category,
            probability_risk=probability_risk,
            measured_or_predicted_value=measured_or_predicted_value,
            unit=unit,
            risk_classification=risk_classification,
            confidence_score=confidence_score,
        )
        self.session.add(ep)
        await self.session.commit()
        await self.session.refresh(ep)
        return ep

    async def add_tox_alert(
        self,
        study_id: UUID,
        alert_name: str,
        substructure_smarts: str,
        mechanism: str,
        severity: str = "MEDIUM",
    ) -> DBStructuralToxAlert:
        alert = DBStructuralToxAlert(
            study_id=study_id,
            alert_name=alert_name,
            substructure_smarts=substructure_smarts,
            mechanism=mechanism,
            severity=severity,
        )
        self.session.add(alert)
        await self.session.commit()
        await self.session.refresh(alert)
        return alert
