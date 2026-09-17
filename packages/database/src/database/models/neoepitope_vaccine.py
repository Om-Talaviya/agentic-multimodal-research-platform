import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base

class DBCancerVaccineDesign(Base):
    __tablename__ = "cancer_vaccine_designs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(100), nullable=False)
    tumor_type = Column(String(100), nullable=False)  # Melanoma, NSCLC, Glioblastoma, Pancreatic
    hla_alleles = Column(JSON, default=list)  # ["HLA-A*02:01", "HLA-A*24:02", "HLA-B*07:02"]
    mrna_construct_sequence = Column(Text, nullable=True)
    polyepitope_junction_cleavability_score = Column(Float, nullable=False, default=0.88)
    predicted_immunogenicity_index = Column(Float, nullable=False, default=0.92)  # 0.0 - 1.0
    properties = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    neoepitopes = relationship("DBCandidateNeoepitope", back_populates="vaccine", cascade="all, delete-orphan")
    schedules = relationship("DBVaccineAdjuvantSchedule", back_populates="vaccine", cascade="all, delete-orphan")

class DBCandidateNeoepitope(Base):
    __tablename__ = "candidate_neoepitopes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vaccine_id = Column(String(36), ForeignKey("cancer_vaccine_designs.id", ondelete="CASCADE"), nullable=False)
    mutated_gene = Column(String(100), nullable=False)  # KRAS, TP53, BRAF, MUC16
    mutation_type = Column(String(50), nullable=False, default="SNV")  # SNV, InDel, Frameshift
    peptide_sequence = Column(String(50), nullable=False)  # 9-11 mer or 15-20 mer
    wildtype_sequence = Column(String(50), nullable=False)
    hla_restriction = Column(String(50), nullable=False)
    mhc_binding_affinity_ic50_nm = Column(Float, nullable=False)  # < 50nM strong binder, < 500nM weak binder
    clonality_vaf_pct = Column(Float, nullable=False)  # Variant Allele Frequency (0-100%)
    expression_tpm = Column(Float, nullable=False)  # RNA-seq TPM expression
    immunogenicity_rank_score = Column(Float, nullable=False)  # 0.0 - 1.0
    is_selected_for_vaccine = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    vaccine = relationship("DBCancerVaccineDesign", back_populates="neoepitopes")

class DBVaccineAdjuvantSchedule(Base):
    __tablename__ = "vaccine_adjuvant_schedules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vaccine_id = Column(String(36), ForeignKey("cancer_vaccine_designs.id", ondelete="CASCADE"), nullable=False)
    adjuvant_type = Column(String(100), nullable=False, default="Poly-ICLC")  # Poly-ICLC (Hiltonol), QS-21, GM-CSF, CpG
    dose_schedule_days = Column(JSON, default=list)  # [0, 3, 7, 14, 28, 56]
    booster_frequency_weeks = Column(Integer, default=4)
    predicted_cd8_tcell_response_pct = Column(Float, nullable=False, default=74.5)  # % of activated CD8+ T cells
    created_at = Column(DateTime, default=datetime.utcnow)

    vaccine = relationship("DBCancerVaccineDesign", back_populates="schedules")
