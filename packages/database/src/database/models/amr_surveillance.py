"""Metagenomic Pathogen Surveillance & Antimicrobial Resistance (AMR) Models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database.connection import Base


class DBMetagenomicSample(Base):
    __tablename__ = "metagenomic_surveillance_samples"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sample_name = Column(String(255), nullable=False)
    sample_type = Column(String(64), default="WASTEWATER")
    collection_location = Column(String(255), default="Municipal Facility A")
    total_reads_sequenced = Column(Integer, default=5000000)
    pathogen_count = Column(Integer, default=4)
    amr_genes_count = Column(Integer, default=6)
    outbreak_risk_level = Column(String(32), default="LOW")
    sample_metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    pathogens = relationship("DBPathogenAbundance", back_populates="sample", cascade="all, delete-orphan")
    amr_genes = relationship("DBAntimicrobialResistanceGene", back_populates="sample", cascade="all, delete-orphan")


class DBPathogenAbundance(Base):
    __tablename__ = "metagenomic_pathogen_abundances"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sample_id = Column(String(36), ForeignKey("metagenomic_surveillance_samples.id", ondelete="CASCADE"), nullable=False)
    taxon_name = Column(String(255), nullable=False)
    ncbi_taxid = Column(Integer, default=0)
    relative_abundance_pct = Column(Float, default=1.0)
    read_depth = Column(Integer, default=1000)
    pathogenicity_grade = Column(String(64), default="OPPORTUNISTIC")
    is_priority_pathogen = Column(Boolean, default=False)

    sample = relationship("DBMetagenomicSample", back_populates="pathogens")


class DBAntimicrobialResistanceGene(Base):
    __tablename__ = "amr_resistance_genes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sample_id = Column(String(36), ForeignKey("metagenomic_surveillance_samples.id", ondelete="CASCADE"), nullable=False)
    gene_symbol = Column(String(128), nullable=False)
    resistance_mechanism = Column(String(128), default="BETA_LACTAMASE")
    drug_class = Column(String(128), default="CARBAPENEMS")
    identity_pct = Column(Float, default=99.0)
    coverage_pct = Column(Float, default=100.0)
    plasmid_mediated = Column(Boolean, default=True)

    sample = relationship("DBMetagenomicSample", back_populates="amr_genes")
