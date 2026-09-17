import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base

class DBCompoundToxicityScreen(Base):
    __tablename__ = "compound_toxicity_screens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    compound_name = Column(String(255), nullable=False)
    smiles_string = Column(Text, nullable=False)
    molecular_weight = Column(Float, nullable=False, default=342.4)
    log_p = Column(Float, nullable=False, default=2.8)
    ames_mutagenicity_status = Column(String(50), nullable=False, default="NEGATIVE")  # POSITIVE, NEGATIVE
    ames_probability_pct = Column(Float, nullable=False, default=12.4)  # 0-100%
    herg_ic50_micromolar = Column(Float, nullable=False, default=24.5)  # IC50 in uM (> 10uM is safe)
    herg_cardiotox_risk = Column(String(50), nullable=False, default="LOW")  # HIGH, MODERATE, LOW
    dili_hepatotox_risk = Column(String(50), nullable=False, default="LOW")  # HIGH, MODERATE, LOW
    ld50_rat_mg_kg = Column(Float, nullable=False, default=1250.0)
    properties = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    structural_alerts = relationship("DBStructuralAlertMatch", back_populates="screen", cascade="all, delete-orphan")

class DBStructuralAlertMatch(Base):
    __tablename__ = "toxicity_structural_alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    screen_id = Column(String(36), ForeignKey("compound_toxicity_screens.id", ondelete="CASCADE"), nullable=False)
    alert_name = Column(String(100), nullable=False)  # Aromatic Amine, Epoxide, Nitroaromatic, Michael Acceptor
    smarts_pattern = Column(String(200), nullable=False)
    toxicophore_category = Column(String(100), nullable=False, default="DNA Alkylating Agent")
    severity_level = Column(String(50), nullable=False, default="HIGH")  # HIGH, MODERATE, LOW
    created_at = Column(DateTime, default=datetime.utcnow)

    screen = relationship("DBCompoundToxicityScreen", back_populates="structural_alerts")
