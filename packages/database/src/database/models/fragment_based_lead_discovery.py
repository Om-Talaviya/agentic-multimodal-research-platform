"""SQLAlchemy models for Phase 184: Fragment-Based Drug Discovery (FBDD) & Linker Growth Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class FBDDLeadDiscoveryStudy(Base):
    """Study record for fragment screening deconstruction, ligand efficiency, and linker growth."""

    __tablename__ = "fbdd_lead_discovery_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_protein_pocket = Column(String(200), nullable=False)
    fragment_library_size = Column(Integer, nullable=False, default=1500)
    top_fragment_kd_micromolar = Column(Float, nullable=False, default=42.5)
    mean_ligand_efficiency = Column(Float, nullable=False, default=0.38)
    linker_growth_strategy = Column(String(100), nullable=False, default="fragment_linking_rigid")
    optimized_lead_predicted_pic50 = Column(Float, nullable=False, default=8.45)
    lipinski_rule_of_three_compliance_pct = Column(Float, nullable=False, default=94.5)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    fragment_hits = relationship("FBDDFragmentHit", back_populates="study", cascade="all, delete-orphan")
    linker_candidates = relationship("FBDDLinkerGrowthCandidate", back_populates="study", cascade="all, delete-orphan")


class FBDDFragmentHit(Base):
    """Identified biophysical fragment hit bound in sub-pocket."""

    __tablename__ = "fbdd_fragment_hits"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("fbdd_lead_discovery_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    fragment_id = Column(String(100), nullable=False)
    smiles_representation = Column(String(255), nullable=False)
    heavy_atom_count = Column(Integer, nullable=False)
    molecular_weight_da = Column(Float, nullable=False)
    dissociation_constant_kd_um = Column(Float, nullable=False)
    ligand_efficiency_le = Column(Float, nullable=False)
    subpocket_binding_site = Column(String(100), nullable=False, default="Pocket-A")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("FBDDLeadDiscoveryStudy", back_populates="fragment_hits")


class FBDDLinkerGrowthCandidate(Base):
    """Synthesized lead candidate formed via fragment merging or linking."""

    __tablename__ = "fbdd_linker_growth_candidates"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("fbdd_lead_discovery_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    lead_id = Column(String(100), nullable=False)
    combined_smiles = Column(String(300), nullable=False)
    linker_type = Column(String(100), nullable=False)
    predicted_affinity_kd_nm = Column(Float, nullable=False)
    binding_delta_g_kcal_mol = Column(Float, nullable=False)
    synthetic_accessibility_sa_score = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("FBDDLeadDiscoveryStudy", back_populates="linker_candidates")