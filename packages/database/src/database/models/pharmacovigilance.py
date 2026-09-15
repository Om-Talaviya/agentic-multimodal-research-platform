"""
Phase 49: Autonomous Real-World Evidence (RWE) & Pharmacovigilance Signal Detector Models.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Float, Integer
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID, JSONType


class DBPharmacovigilanceCorpus(Base):
    __tablename__ = "pv_surveillance_corpora"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(500), nullable=False)
    data_sources = Column(JSONType, default=lambda: ["FDA_FAERS", "WHO_VigiBase", "EudraVigilance", "EHR_Claims"])
    total_adverse_reports = Column(Integer, default=1250000)
    status = Column(String(50), default="ANALYZED")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    signals = relationship("DBSafetySignalReport", back_populates="corpus", cascade="all, delete-orphan")


class DBSafetySignalReport(Base):
    __tablename__ = "pv_safety_signals"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    corpus_id = Column(GUID, ForeignKey("pv_surveillance_corpora.id", ondelete="CASCADE"), nullable=False)
    drug_name = Column(String(255), nullable=False)
    adverse_reaction_term = Column(String(255), nullable=False) # MedDRA Preferred Term
    system_organ_class = Column(String(255), default="Cardiac disorders")
    case_count = Column(Integer, default=142)
    signal_priority = Column(String(50), default="ELEVATED") # URGENT, ELEVATED, ROUTINE
    who_umc_causality = Column(String(50), default="Probable") # Certain, Probable, Possible, Unlikely
    clinical_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    corpus = relationship("DBPharmacovigilanceCorpus", back_populates="signals")
    metrics = relationship("DBDisproportionalityMetric", back_populates="signal", cascade="all, delete-orphan")


class DBDisproportionalityMetric(Base):
    __tablename__ = "pv_disproportionality_metrics"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    signal_id = Column(GUID, ForeignKey("pv_safety_signals.id", ondelete="CASCADE"), nullable=False)
    proportional_reporting_ratio_prr = Column(Float, default=3.45)
    reporting_odds_ratio_ror = Column(Float, default=3.62)
    ror_ci_lower_95 = Column(Float, default=2.85)
    ror_ci_upper_95 = Column(Float, default=4.55)
    information_component_ic025 = Column(Float, default=1.65) # BCPNN lower 95% bound
    ebgm_05 = Column(Float, default=3.20) # MGPS lower 90% bound
    chi_square_yates = Column(Float, default=48.6)
    created_at = Column(DateTime, default=datetime.utcnow)

    signal = relationship("DBSafetySignalReport", back_populates="metrics")
