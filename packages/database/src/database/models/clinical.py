"""Clinical Trial Protocol & Drug Repurposing Database Models (Phase 36)."""

import uuid
from datetime import UTC, datetime
from typing import Optional
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID, JSONType


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBClinicalProtocol(Base):
    """Clinical trial protocol specification entity."""

    __tablename__ = "clinical_protocols"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id = Column(GUID(), ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True, index=True)
    project_id = Column(GUID(), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)

    protocol_title = Column(String(300), nullable=False)
    phase_type = Column(String(50), nullable=False, default="Phase I/IIa")  # Phase I, Phase I/IIa, Phase IIb, Phase III, IND-Enabling
    disease_indication = Column(String(200), nullable=False, index=True)
    icd_code = Column(String(50), nullable=True)
    investigational_agent = Column(String(200), nullable=False, index=True)
    mechanism_of_action = Column(Text, nullable=True)
    target_gene_or_protein = Column(String(100), nullable=True, index=True)
    primary_endpoint = Column(Text, nullable=False)
    secondary_endpoints = Column(JSONType, nullable=False, default=list)  # List[str]
    sample_size_planned = Column(Integer, nullable=False, default=48)
    study_duration_weeks = Column(Integer, nullable=False, default=52)
    adverse_risk_score = Column(Float, nullable=False, default=0.15)  # 0.0 to 1.0
    regulatory_status = Column(String(50), nullable=False, default="draft")  # draft, irb_submitted, fda_ind_cleared, active

    full_protocol_json = Column(JSONType, nullable=False, default=dict)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    cohort_criteria = relationship(
        "DBCohortCriterion",
        back_populates="protocol",
        cascade="all, delete-orphan",
        order_by="DBCohortCriterion.criterion_type",
    )
    drug_candidates = relationship(
        "DBDrugCandidate",
        back_populates="protocol",
        cascade="all, delete-orphan",
    )
    regulatory_packages = relationship(
        "DBRegulatoryPackage",
        back_populates="protocol",
        cascade="all, delete-orphan",
    )


class DBCohortCriterion(Base):
    """Fine-grained patient inclusion/exclusion criteria for clinical cohorts."""

    __tablename__ = "clinical_cohort_criteria"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    protocol_id = Column(GUID(), ForeignKey("clinical_protocols.id", ondelete="CASCADE"), nullable=False, index=True)

    criterion_type = Column(String(20), nullable=False, index=True)  # inclusion, exclusion
    category = Column(String(50), nullable=False, default="diagnostic")  # demographic, diagnostic, biomarker, prior_therapy, safety
    description = Column(Text, nullable=False)
    is_mandatory = Column(Boolean, nullable=False, default=True)
    loinc_code = Column(String(50), nullable=True)

    # Relationships
    protocol = relationship("DBClinicalProtocol", back_populates="cohort_criteria")


class DBDrugCandidate(Base):
    """Repurposed drug candidate screened against disease target."""

    __tablename__ = "clinical_drug_candidates"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    protocol_id = Column(GUID(), ForeignKey("clinical_protocols.id", ondelete="SET NULL"), nullable=True, index=True)

    compound_name = Column(String(200), nullable=False, index=True)
    smiles_string = Column(Text, nullable=True)
    current_approved_indication = Column(String(200), nullable=False)
    repurposed_indication = Column(String(200), nullable=False)
    binding_affinity_nm = Column(Float, nullable=False, default=12.5)  # Kd / Ki in nanomolar
    bioavailability_pct = Column(Float, nullable=False, default=78.0)
    toxicity_risk_score = Column(Float, nullable=False, default=0.12)  # 0.0 - 1.0
    repurposing_rationale = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    protocol = relationship("DBClinicalProtocol", back_populates="drug_candidates")


class DBRegulatoryPackage(Base):
    """FDA IND / EMA CTD Regulatory submission dossier module."""

    __tablename__ = "clinical_regulatory_packages"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    protocol_id = Column(GUID(), ForeignKey("clinical_protocols.id", ondelete="CASCADE"), nullable=False, index=True)

    regulatory_agency = Column(String(50), nullable=False, default="FDA")  # FDA, EMA, PMDA, MHRA
    module_type = Column(String(50), nullable=False, default="IND Module 2")  # IND Module 2, IND Module 4 Nonclinical, IND Module 5 Clinical
    completeness_score = Column(Float, nullable=False, default=0.92)  # 0.0 - 1.0
    irb_readiness_verdict = Column(String(50), nullable=False, default="ready")  # ready, needs_revision, blocked
    validation_findings = Column(JSONType, nullable=False, default=list)

    generated_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    protocol = relationship("DBClinicalProtocol", back_populates="regulatory_packages")
