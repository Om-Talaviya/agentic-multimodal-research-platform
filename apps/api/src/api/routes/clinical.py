"""Autonomous Clinical Trial Protocol & Drug Repurposing API Routes (Phase 36)."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db_session
from database.models.user import User as DBUser
from database.repositories.clinical_repo import ClinicalRepository
from research.clinical_trial_engine import ClinicalTrialEngine
from shared.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/clinical", tags=["clinical-trials"])
engine = ClinicalTrialEngine()


# --- Pydantic Request / Response Schemas ---

class ProtocolGenerateRequest(BaseModel):
    disease_indication: str = Field(..., description="Target disease or pathology (e.g., Familial Hypercholesterolemia)")
    investigational_agent: str = Field(..., description="Investigational drug or modality (e.g., LNP-dCas9-Epi)")
    target_gene_or_protein: Optional[str] = Field(None, description="Molecular target (e.g., PCSK9, TTR, HBB)")
    phase_type: str = Field("Phase I/IIa", description="Clinical phase classification")
    mechanism_of_action: Optional[str] = Field(None, description="Biological mechanism of action")
    workspace_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None


class AddCohortCriterionRequest(BaseModel):
    criterion_type: str = Field(..., description="'inclusion' or 'exclusion'")
    category: str = Field("diagnostic", description="demographic, diagnostic, biomarker, prior_therapy, safety")
    description: str = Field(..., description="Detailed medical eligibility statement")
    is_mandatory: bool = True
    loinc_code: Optional[str] = None


class RepurposeScreenRequest(BaseModel):
    disease_indication: str
    target_gene_or_protein: Optional[str] = None


class GenerateRegulatoryPackageRequest(BaseModel):
    regulatory_agency: str = Field("FDA", description="Target agency: FDA, EMA, PMDA, MHRA")


# --- Endpoint Implementations ---

@router.post("/protocols/generate", status_code=status.HTTP_201_CREATED)
async def generate_clinical_protocol(
    payload: ProtocolGenerateRequest,
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Autonomous Generation of a GCP/FDA-Compliant Clinical Trial Protocol."""
    spec = engine.synthesize_protocol(
        disease_indication=payload.disease_indication,
        investigational_agent=payload.investigational_agent,
        target_gene_or_protein=payload.target_gene_or_protein,
        phase_type=payload.phase_type,
        mechanism_of_action=payload.mechanism_of_action,
    )

    repo = ClinicalRepository(session)
    protocol = await repo.create_protocol(
        user_id=current_user.id,
        workspace_id=payload.workspace_id,
        project_id=payload.project_id,
        protocol_title=spec["protocol_title"],
        phase_type=spec["phase_type"],
        disease_indication=spec["disease_indication"],
        icd_code=spec["icd_code"],
        investigational_agent=spec["investigational_agent"],
        mechanism_of_action=spec["mechanism_of_action"],
        target_gene_or_protein=spec["target_gene_or_protein"],
        primary_endpoint=spec["primary_endpoint"],
        secondary_endpoints=spec["secondary_endpoints"],
        sample_size_planned=spec["sample_size_planned"],
        study_duration_weeks=spec["study_duration_weeks"],
        adverse_risk_score=spec["adverse_risk_score"],
        full_protocol_json=spec["full_protocol_json"],
    )

    # Persist initial synthesized cohort criteria
    for crit in spec["cohort_criteria"]:
        await repo.add_cohort_criterion(
            protocol_id=protocol.id,
            criterion_type=crit["criterion_type"],
            category=crit["category"],
            description=crit["description"],
            is_mandatory=crit["is_mandatory"],
            loinc_code=crit.get("loinc_code"),
        )

    # Screen initial drug repurposing adjuvants
    candidates = engine.screen_repurposing_candidates(
        disease_indication=payload.disease_indication,
        target_gene_or_protein=payload.target_gene_or_protein,
    )
    for cand in candidates:
        await repo.add_drug_candidate(
            protocol_id=protocol.id,
            compound_name=cand["compound_name"],
            smiles_string=cand.get("smiles_string"),
            current_approved_indication=cand["current_approved_indication"],
            repurposed_indication=cand["repurposed_indication"],
            binding_affinity_nm=cand["binding_affinity_nm"],
            bioavailability_pct=cand["bioavailability_pct"],
            toxicity_risk_score=cand["toxicity_risk_score"],
            repurposing_rationale=cand["repurposing_rationale"],
        )

    # Generate initial FDA IND package
    reg = engine.generate_regulatory_package(spec, regulatory_agency="FDA")
    await repo.create_regulatory_package(
        protocol_id=protocol.id,
        regulatory_agency=reg["regulatory_agency"],
        module_type=reg["module_type"],
        completeness_score=reg["completeness_score"],
        irb_readiness_verdict=reg["irb_readiness_verdict"],
        validation_findings=reg["validation_findings"],
    )

    await session.commit()
    fresh = await repo.get_protocol(protocol.id)

    return {
        "protocol_id": str(protocol.id),
        "protocol_title": protocol.protocol_title,
        "phase_type": protocol.phase_type,
        "disease_indication": protocol.disease_indication,
        "investigational_agent": protocol.investigational_agent,
        "primary_endpoint": protocol.primary_endpoint,
        "secondary_endpoints": protocol.secondary_endpoints,
        "sample_size_planned": protocol.sample_size_planned,
        "adverse_risk_score": protocol.adverse_risk_score,
        "cohort_criteria_count": len(fresh.cohort_criteria) if fresh else 0,
        "drug_candidates_count": len(fresh.drug_candidates) if fresh else 0,
        "regulatory_packages_count": len(fresh.regulatory_packages) if fresh else 0,
    }


@router.get("/protocols")
async def list_clinical_protocols(
    workspace_id: Optional[uuid.UUID] = None,
    project_id: Optional[uuid.UUID] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """List clinical trial protocols."""
    repo = ClinicalRepository(session)
    protocols = await repo.list_protocols(
        user_id=current_user.id,
        workspace_id=workspace_id,
        project_id=project_id,
        limit=limit,
        offset=offset,
    )
    return {
        "protocols": [
            {
                "id": str(p.id),
                "protocol_title": p.protocol_title,
                "phase_type": p.phase_type,
                "disease_indication": p.disease_indication,
                "investigational_agent": p.investigational_agent,
                "sample_size_planned": p.sample_size_planned,
                "regulatory_status": p.regulatory_status,
                "adverse_risk_score": p.adverse_risk_score,
                "criteria_count": len(p.cohort_criteria),
                "candidates_count": len(p.drug_candidates),
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in protocols
        ],
        "total": len(protocols),
    }


@router.get("/protocols/{protocol_id}")
async def get_clinical_protocol_details(
    protocol_id: uuid.UUID,
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Retrieve full clinical protocol with cohort criteria, candidates, and regulatory dossiers."""
    repo = ClinicalRepository(session)
    protocol = await repo.get_protocol(protocol_id)
    if not protocol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clinical protocol '{protocol_id}' not found.",
        )

    return {
        "id": str(protocol.id),
        "protocol_title": protocol.protocol_title,
        "phase_type": protocol.phase_type,
        "disease_indication": protocol.disease_indication,
        "icd_code": protocol.icd_code,
        "investigational_agent": protocol.investigational_agent,
        "mechanism_of_action": protocol.mechanism_of_action,
        "target_gene_or_protein": protocol.target_gene_or_protein,
        "primary_endpoint": protocol.primary_endpoint,
        "secondary_endpoints": protocol.secondary_endpoints,
        "sample_size_planned": protocol.sample_size_planned,
        "study_duration_weeks": protocol.study_duration_weeks,
        "adverse_risk_score": protocol.adverse_risk_score,
        "regulatory_status": protocol.regulatory_status,
        "cohort_criteria": [
            {
                "id": str(c.id),
                "criterion_type": c.criterion_type,
                "category": c.category,
                "description": c.description,
                "is_mandatory": c.is_mandatory,
                "loinc_code": c.loinc_code,
            }
            for c in protocol.cohort_criteria
        ],
        "drug_candidates": [
            {
                "id": str(d.id),
                "compound_name": d.compound_name,
                "smiles_string": d.smiles_string,
                "current_approved_indication": d.current_approved_indication,
                "repurposed_indication": d.repurposed_indication,
                "binding_affinity_nm": d.binding_affinity_nm,
                "bioavailability_pct": d.bioavailability_pct,
                "toxicity_risk_score": d.toxicity_risk_score,
                "repurposing_rationale": d.repurposing_rationale,
            }
            for d in protocol.drug_candidates
        ],
        "regulatory_packages": [
            {
                "id": str(r.id),
                "regulatory_agency": r.regulatory_agency,
                "module_type": r.module_type,
                "completeness_score": r.completeness_score,
                "irb_readiness_verdict": r.irb_readiness_verdict,
                "validation_findings": r.validation_findings,
                "generated_at": r.generated_at.isoformat() if r.generated_at else None,
            }
            for r in protocol.regulatory_packages
        ],
        "full_protocol_json": protocol.full_protocol_json,
        "created_at": protocol.created_at.isoformat() if protocol.created_at else None,
    }


@router.post("/protocols/{protocol_id}/criteria", status_code=status.HTTP_201_CREATED)
async def add_cohort_criterion(
    protocol_id: uuid.UUID,
    payload: AddCohortCriterionRequest,
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Add a fine-grained patient cohort inclusion or exclusion criterion."""
    repo = ClinicalRepository(session)
    protocol = await repo.get_protocol(protocol_id)
    if not protocol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clinical protocol '{protocol_id}' not found.",
        )

    crit = await repo.add_cohort_criterion(
        protocol_id=protocol_id,
        criterion_type=payload.criterion_type,
        description=payload.description,
        category=payload.category,
        is_mandatory=payload.is_mandatory,
        loinc_code=payload.loinc_code,
    )
    await session.commit()

    return {
        "id": str(crit.id),
        "protocol_id": str(protocol_id),
        "criterion_type": crit.criterion_type,
        "category": crit.category,
        "description": crit.description,
        "is_mandatory": crit.is_mandatory,
    }


@router.post("/protocols/{protocol_id}/regulatory-package", status_code=status.HTTP_201_CREATED)
async def generate_regulatory_package_endpoint(
    protocol_id: uuid.UUID,
    payload: GenerateRegulatoryPackageRequest,
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Generate an eCTD IND regulatory module package for the protocol."""
    repo = ClinicalRepository(session)
    protocol = await repo.get_protocol(protocol_id)
    if not protocol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clinical protocol '{protocol_id}' not found.",
        )

    proto_dict = {
        "protocol_title": protocol.protocol_title,
        "primary_endpoint": protocol.primary_endpoint,
        "adverse_risk_score": protocol.adverse_risk_score,
        "cohort_criteria": [{"criterion_type": c.criterion_type} for c in protocol.cohort_criteria],
    }
    reg = engine.generate_regulatory_package(proto_dict, regulatory_agency=payload.regulatory_agency)

    pkg = await repo.create_regulatory_package(
        protocol_id=protocol_id,
        regulatory_agency=reg["regulatory_agency"],
        module_type=reg["module_type"],
        completeness_score=reg["completeness_score"],
        irb_readiness_verdict=reg["irb_readiness_verdict"],
        validation_findings=reg["validation_findings"],
    )
    await session.commit()

    return {
        "id": str(pkg.id),
        "protocol_id": str(protocol_id),
        "regulatory_agency": pkg.regulatory_agency,
        "module_type": pkg.module_type,
        "completeness_score": pkg.completeness_score,
        "irb_readiness_verdict": pkg.irb_readiness_verdict,
        "validation_findings": pkg.validation_findings,
    }
