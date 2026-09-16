"""
SQLAlchemy models for Autonomous Computational Immunology & TCR-pMHC Neoantigen Binding Predictor (Phase 55).
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship

from database.connection import Base


class DBNeoantigenScreen(Base):
    """Represents a personalized neoantigen screening and epitope prioritization campaign."""
    __tablename__ = "immunology_screens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(64), nullable=False)
    tumor_type = Column(String(128), nullable=False)  # e.g., Melanoma, NSCLC
    hla_alleles = Column(JSON, nullable=False, default=list)  # e.g., ["HLA-A*02:01", "HLA-B*07:02"]
    mutation_count = Column(Integer, default=0)
    top_candidates_count = Column(Integer, default=0)
    status = Column(String(32), default="COMPLETED")
    metadata_info = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    epitopes = relationship("DBNeoantigenEpitope", back_populates="screen", cascade="all, delete-orphan")
    vaccine_constructs = relationship("DBVaccineConstructDesign", back_populates="screen", cascade="all, delete-orphan")


class DBNeoantigenEpitope(Base):
    """Represents an identified peptide epitope evaluated for HLA presentation and TCR reactivity."""
    __tablename__ = "immunology_epitopes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    screen_id = Column(String(36), ForeignKey("immunology_screens.id", ondelete="CASCADE"), nullable=False)
    gene_symbol = Column(String(64), nullable=False)  # e.g., TP53, KRAS
    mutation_variant = Column(String(64), nullable=False)  # e.g., G12D, R175H
    peptide_sequence = Column(String(32), nullable=False)  # e.g., 9-mer or 10-mer
    wildtype_sequence = Column(String(32), nullable=True)
    hla_allele = Column(String(32), nullable=False)  # e.g., HLA-A*02:01
    binding_ic50_nm = Column(Float, nullable=False)  # <500 nM strong, <50nM very strong
    percentile_rank = Column(Float, nullable=False)  # % rank relative to random peptides
    tcr_immunogenicity_score = Column(Float, nullable=False)  # 0.0 - 1.0
    proteasomal_cleavage_score = Column(Float, default=0.85)
    tap_transport_efficiency = Column(Float, default=0.90)
    composite_priority_score = Column(Float, nullable=False)
    recommended_for_vaccine = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    screen = relationship("DBNeoantigenScreen", back_populates="epitopes")


class DBVaccineConstructDesign(Base):
    """Represents an automated multi-epitope mRNA or peptide vaccine construct design."""
    __tablename__ = "immunology_vaccine_constructs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    screen_id = Column(String(36), ForeignKey("immunology_screens.id", ondelete="CASCADE"), nullable=False)
    construct_name = Column(String(128), nullable=False)
    construct_type = Column(String(32), default="mRNA_LNP")  # mRNA_LNP, Synthetic_Peptide, Dendritic_Cell
    ordered_epitopes = Column(JSON, nullable=False, default=list)  # list of peptide IDs / sequences
    linker_sequences = Column(JSON, nullable=False, default=list)  # e.g. ["AAY", "GPGPG"]
    full_polyepitope_sequence = Column(Text, nullable=False)
    junctional_immunogenicity_risk = Column(Float, default=0.05)  # low risk is better
    predicted_expression_efficiency = Column(Float, default=0.92)
    created_at = Column(DateTime, default=datetime.utcnow)

    screen = relationship("DBNeoantigenScreen", back_populates="vaccine_constructs")
