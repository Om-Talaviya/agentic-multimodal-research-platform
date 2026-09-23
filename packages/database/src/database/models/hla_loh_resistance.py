"""
Phase 135: Cancer Immunogenomics HLA Loss of Heterozygosity (LOH) & Immune Evasion Database Models.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID, JSON


class DBHLALOHStudy(Base):
    __tablename__ = "hla_loh_studies"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID, nullable=True, index=True)
    patient_cohort_id = Column(String(255), nullable=False, index=True)
    tumor_type = Column(String(255), nullable=False)
    total_alleles_analyzed = Column(Integer, nullable=False, default=6)
    loh_positive_allele_count = Column(Integer, nullable=False, default=2)
    overall_immune_evasion_index = Column(Float, nullable=False, default=0.74)
    checkpoint_resistance_prediction = Column(String(100), nullable=False, default="High Resistance")
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    allele_profiles = relationship(
        "DBAlleleCopyNumberProfile",
        back_populates="study",
        cascade="all, delete-orphan",
    )
    evasion_scores = relationship(
        "DBImmuneEvasionScore",
        back_populates="study",
        cascade="all, delete-orphan",
    )


class DBAlleleCopyNumberProfile(Base):
    __tablename__ = "allele_copy_number_profiles"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID, ForeignKey("hla_loh_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    hla_gene = Column(String(50), nullable=False)  # "HLA-A", "HLA-B", "HLA-C"
    allele_identifier = Column(String(100), nullable=False)  # "HLA-A*02:01"
    tumor_copy_number = Column(Float, nullable=False)
    germline_copy_number = Column(Float, nullable=False, default=1.0)
    b_allele_frequency_baf = Column(Float, nullable=False)
    loh_status = Column(String(50), nullable=False)  # "DELETED", "RETAINED", "AMPLIFIED"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    study = relationship("DBHLALOHStudy", back_populates="allele_profiles")


class DBImmuneEvasionScore(Base):
    __tablename__ = "immune_evasion_scores"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID, ForeignKey("hla_loh_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    neoantigen_presentation_loss_percent = Column(Float, nullable=False)
    cd8_t_cell_evasion_probability = Column(Float, nullable=False)
    nk_cell_activation_potential = Column(Float, nullable=False)
    recommended_synthetic_rescue = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    study = relationship("DBHLALOHStudy", back_populates="evasion_scores")
