"""
SQLAlchemy models for Rare Disease Phenotype-to-Genotype Matching & HPO Engine (Phase 61).
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


class DBRareDiseaseDiagnosticCase(Base):
    """Represents an undiagnosed rare disease clinical case."""
    __tablename__ = "rare_disease_cases"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_number = Column(String(64), nullable=False)
    patient_id = Column(String(64), nullable=False)
    clinical_summary = Column(Text, nullable=False)
    age_of_onset = Column(String(32), default="Infantile")  # Congenital, Infantile, Juvenile, Adult
    total_phenotypes_mapped = Column(Integer, default=0)
    top_predicted_disease = Column(String(128), nullable=True)
    status = Column(String(32), default="RESOLVED")
    metadata_info = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    phenotypes = relationship("DBHPOPhenotypeTerm", back_populates="case", cascade="all, delete-orphan")
    candidate_genes = relationship("DBCandidateGeneMatch", back_populates="case", cascade="all, delete-orphan")


class DBHPOPhenotypeTerm(Base):
    """Represents an extracted Human Phenotype Ontology (HPO) term."""
    __tablename__ = "rare_disease_hpo_terms"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String(36), ForeignKey("rare_disease_cases.id", ondelete="CASCADE"), nullable=False)
    hpo_id = Column(String(32), nullable=False)  # HP:0001250
    term_name = Column(String(128), nullable=False)  # Seizures, Hypotonia, Microcephaly
    severity_weight = Column(Float, default=1.0)
    is_negated = Column(Boolean, default=False)
    information_content = Column(Float, default=7.5)  # Resnik Information Content
    created_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("DBRareDiseaseDiagnosticCase", back_populates="phenotypes")


class DBCandidateGeneMatch(Base):
    """Represents a candidate causal gene matching the patient's HPO phenotype profile."""
    __tablename__ = "rare_disease_candidate_genes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String(36), ForeignKey("rare_disease_cases.id", ondelete="CASCADE"), nullable=False)
    gene_symbol = Column(String(64), nullable=False)  # SCN1A, MECP2, CDKL5, PAH
    disease_name = Column(String(128), nullable=False)  # Dravet syndrome, Rett syndrome
    omim_id = Column(String(16), default="OMIM:607208")
    semantic_similarity_score = Column(Float, nullable=False)  # 0.0 - 1.0
    inheritance_mode = Column(String(64), default="Autosomal Dominant")
    pathogenicity_evidence = Column(String(128), default="ClinVar 3-Star Pathogenic")
    is_top_match = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("DBRareDiseaseDiagnosticCase", back_populates="candidate_genes")
