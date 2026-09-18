"""Preclinical Toxicogenomics & ADMET Safety Risk Database Models."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID


class DBPreclinicalToxStudy(Base):
    __tablename__ = "preclinical_tox_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), nullable=False, index=True)
    compound_name = Column(String(255), nullable=False)
    smiles_string = Column(Text, nullable=False)
    therapeutic_safety_index = Column(Float, default=75.0, nullable=False)  # 0 to 100
    overall_safety_tier = Column(String(50), default="FAVORABLE", nullable=False)  # FAVORABLE, MODERATE_RISK, HIGH_RISK, CRITICAL
    caco2_permeability_cm_s = Column(Float, default=1.5e-5, nullable=False)
    plasma_protein_binding_pct = Column(Float, default=88.5, nullable=False)
    study_metadata = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    endpoints = relationship("DBToxicogenomicEndpoint", back_populates="study", cascade="all, delete-orphan")
    tox_alerts = relationship("DBStructuralToxAlert", back_populates="study", cascade="all, delete-orphan")


class DBToxicogenomicEndpoint(Base):
    __tablename__ = "toxicogenomic_endpoints"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("preclinical_tox_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    endpoint_name = Column(String(100), nullable=False)  # Ames, hERG, DILI, CYP3A4, CYP2D6
    endpoint_category = Column(String(100), default="Organ Toxicity", nullable=False)  # Cardiotoxicity, Hepatotoxicity, Mutagenicity, Metabolism
    probability_risk = Column(Float, nullable=False)  # 0.0 to 1.0
    measured_or_predicted_value = Column(Float, nullable=False)
    unit = Column(String(50), default="uM", nullable=False)
    risk_classification = Column(String(50), default="LOW", nullable=False)  # LOW, MODERATE, HIGH
    confidence_score = Column(Float, default=0.90, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    study = relationship("DBPreclinicalToxStudy", back_populates="endpoints")


class DBStructuralToxAlert(Base):
    __tablename__ = "structural_tox_alerts"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("preclinical_tox_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    alert_name = Column(String(255), nullable=False)  # e.g., Michael Acceptor, Quinone Imine Precursor
    substructure_smarts = Column(String(255), nullable=False)
    mechanism = Column(String(255), nullable=False)
    severity = Column(String(50), default="MEDIUM", nullable=False)  # LOW, MEDIUM, HIGH, FLAGGED
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    study = relationship("DBPreclinicalToxStudy", back_populates="tox_alerts")
