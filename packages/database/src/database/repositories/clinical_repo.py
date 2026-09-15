"""Clinical Trial & Drug Repurposing Repository (Phase 36)."""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.clinical import (
    DBClinicalProtocol,
    DBCohortCriterion,
    DBDrugCandidate,
    DBRegulatoryPackage,
)
from shared.logging import get_logger

logger = get_logger(__name__)


class ClinicalRepository:
    """Async repository for clinical trial protocols, cohort criteria, and drug candidates."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_protocol(
        self,
        user_id: uuid.UUID | str,
        protocol_title: str,
        disease_indication: str,
        investigational_agent: str,
        primary_endpoint: str,
        phase_type: str = "Phase I/IIa",
        icd_code: Optional[str] = None,
        mechanism_of_action: Optional[str] = None,
        target_gene_or_protein: Optional[str] = None,
        secondary_endpoints: Optional[List[str]] = None,
        sample_size_planned: int = 48,
        study_duration_weeks: int = 52,
        adverse_risk_score: float = 0.15,
        workspace_id: Optional[uuid.UUID | str] = None,
        project_id: Optional[uuid.UUID | str] = None,
        full_protocol_json: Optional[Dict[str, Any]] = None,
    ) -> DBClinicalProtocol:
        """Create and persist a new clinical protocol specification."""
        protocol = DBClinicalProtocol(
            id=uuid.uuid4(),
            user_id=user_id,
            workspace_id=workspace_id,
            project_id=project_id,
            protocol_title=protocol_title,
            phase_type=phase_type,
            disease_indication=disease_indication,
            icd_code=icd_code,
            investigational_agent=investigational_agent,
            mechanism_of_action=mechanism_of_action,
            target_gene_or_protein=target_gene_or_protein,
            primary_endpoint=primary_endpoint,
            secondary_endpoints=secondary_endpoints or [],
            sample_size_planned=sample_size_planned,
            study_duration_weeks=study_duration_weeks,
            adverse_risk_score=adverse_risk_score,
            regulatory_status="draft",
            full_protocol_json=full_protocol_json or {},
        )
        self._session.add(protocol)
        await self._session.flush()
        logger.info("clinical_protocol_created", protocol_id=str(protocol.id), title=protocol_title)
        return protocol

    async def get_protocol(self, protocol_id: uuid.UUID | str) -> Optional[DBClinicalProtocol]:
        """Fetch a clinical protocol by ID with all cohort criteria, drug candidates, and regulatory packages."""
        stmt = (
            select(DBClinicalProtocol)
            .where(DBClinicalProtocol.id == protocol_id)
            .options(
                selectinload(DBClinicalProtocol.cohort_criteria),
                selectinload(DBClinicalProtocol.drug_candidates),
                selectinload(DBClinicalProtocol.regulatory_packages),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def list_protocols(
        self,
        user_id: Optional[uuid.UUID | str] = None,
        workspace_id: Optional[uuid.UUID | str] = None,
        project_id: Optional[uuid.UUID | str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DBClinicalProtocol]:
        """List clinical protocols filtered by user, workspace, or project."""
        stmt = select(DBClinicalProtocol).options(
            selectinload(DBClinicalProtocol.cohort_criteria),
            selectinload(DBClinicalProtocol.drug_candidates),
            selectinload(DBClinicalProtocol.regulatory_packages),
        ).order_by(desc(DBClinicalProtocol.created_at)).limit(limit).offset(offset)

        if project_id:
            stmt = stmt.where(DBClinicalProtocol.project_id == project_id)
        elif workspace_id:
            stmt = stmt.where(DBClinicalProtocol.workspace_id == workspace_id)
        elif user_id:
            stmt = stmt.where(DBClinicalProtocol.user_id == user_id)

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def add_cohort_criterion(
        self,
        protocol_id: uuid.UUID | str,
        criterion_type: str,
        description: str,
        category: str = "diagnostic",
        is_mandatory: bool = True,
        loinc_code: Optional[str] = None,
    ) -> DBCohortCriterion:
        """Add an inclusion or exclusion criterion to a protocol."""
        criterion = DBCohortCriterion(
            id=uuid.uuid4(),
            protocol_id=protocol_id,
            criterion_type=criterion_type.lower(),
            description=description,
            category=category,
            is_mandatory=is_mandatory,
            loinc_code=loinc_code,
        )
        self._session.add(criterion)
        await self._session.flush()
        return criterion

    async def add_drug_candidate(
        self,
        compound_name: str,
        current_approved_indication: str,
        repurposed_indication: str,
        repurposing_rationale: str,
        protocol_id: Optional[uuid.UUID | str] = None,
        smiles_string: Optional[str] = None,
        binding_affinity_nm: float = 12.5,
        bioavailability_pct: float = 78.0,
        toxicity_risk_score: float = 0.12,
    ) -> DBDrugCandidate:
        """Register a drug candidate identified for repositioning."""
        candidate = DBDrugCandidate(
            id=uuid.uuid4(),
            protocol_id=protocol_id,
            compound_name=compound_name,
            smiles_string=smiles_string,
            current_approved_indication=current_approved_indication,
            repurposed_indication=repurposed_indication,
            binding_affinity_nm=binding_affinity_nm,
            bioavailability_pct=bioavailability_pct,
            toxicity_risk_score=toxicity_risk_score,
            repurposing_rationale=repurposing_rationale,
        )
        self._session.add(candidate)
        await self._session.flush()
        return candidate

    async def list_drug_candidates(
        self,
        protocol_id: Optional[uuid.UUID | str] = None,
        limit: int = 50,
    ) -> List[DBDrugCandidate]:
        """List drug repurposing candidates."""
        stmt = select(DBDrugCandidate).order_by(desc(DBDrugCandidate.created_at)).limit(limit)
        if protocol_id:
            stmt = stmt.where(DBDrugCandidate.protocol_id == protocol_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create_regulatory_package(
        self,
        protocol_id: uuid.UUID | str,
        regulatory_agency: str = "FDA",
        module_type: str = "IND Module 2",
        completeness_score: float = 0.92,
        irb_readiness_verdict: str = "ready",
        validation_findings: Optional[List[Dict[str, Any]]] = None,
    ) -> DBRegulatoryPackage:
        """Create a regulatory submission compliance package."""
        pkg = DBRegulatoryPackage(
            id=uuid.uuid4(),
            protocol_id=protocol_id,
            regulatory_agency=regulatory_agency,
            module_type=module_type,
            completeness_score=completeness_score,
            irb_readiness_verdict=irb_readiness_verdict,
            validation_findings=validation_findings or [],
        )
        self._session.add(pkg)
        await self._session.flush()
        return pkg
