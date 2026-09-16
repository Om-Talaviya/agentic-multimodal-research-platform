import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base

class DBCARTConstructDesign(Base):
    __tablename__ = "cart_construct_designs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    construct_name = Column(String(255), nullable=False)
    target_antigen = Column(String(100), nullable=False) # CD19, BCMA, HER2, EGFRvIII, PSMA
    scfv_binder_clone = Column(String(100), nullable=False) # FMC63, 11D5-3, 4D5
    costimulatory_domain = Column(String(100), nullable=False) # 4-1BB (CD137), CD28, CD28+4-1BB (3rd Gen)
    hinge_transmembrane = Column(String(100), nullable=False, default="CD8a") # CD8a, IgG4-Fc
    signaling_domain = Column(String(100), nullable=False, default="CD3zeta")
    vector_type = Column(String(50), nullable=False, default="Lentiviral") # Lentiviral, Retroviral, AAV, mRNA-LNP
    full_aa_sequence = Column(Text, nullable=True)
    properties = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    cytotoxicity_scorecards = relationship("DBCYToxicityScorecard", back_populates="construct", cascade="all, delete-orphan")
    crs_profiles = relationship("DBCRSToxicityProfile", back_populates="construct", cascade="all, delete-orphan")

class DBCYToxicityScorecard(Base):
    __tablename__ = "cart_cytotoxicity_scorecards"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    construct_id = Column(String(36), ForeignKey("cart_construct_designs.id", ondelete="CASCADE"), nullable=False)
    target_cell_line = Column(String(100), nullable=False) # Raji, Nalm-6, K562-CD19, MM.1S
    effector_to_target_ratio = Column(Float, nullable=False, default=5.0) # E:T (e.g. 1:1, 5:1, 10:1)
    specific_lysis_pct = Column(Float, nullable=False) # 0-100%
    t_cell_persistence_score = Column(Float, nullable=False) # 0-1 (stem central memory Tcm fraction)
    exhaustion_pd1_expression_pct = Column(Float, nullable=False) # % PD-1+
    exhaustion_tim3_expression_pct = Column(Float, nullable=False) # % TIM-3+
    exhaustion_lag3_expression_pct = Column(Float, nullable=False) # % LAG-3+
    cytotoxicity_grade = Column(String(50), nullable=False, default="HIGH") # POTENT, HIGH, MODERATE, LOW
    created_at = Column(DateTime, default=datetime.utcnow)

    construct = relationship("DBCARTConstructDesign", back_populates="cytotoxicity_scorecards")

class DBCRSToxicityProfile(Base):
    __tablename__ = "cart_crs_toxicity_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    construct_id = Column(String(36), ForeignKey("cart_construct_designs.id", ondelete="CASCADE"), nullable=False)
    peak_il6_pg_ml = Column(Float, nullable=False) # Interleukin-6 peak
    peak_ifng_pg_ml = Column(Float, nullable=False) # Interferon-gamma peak
    peak_tnfa_pg_ml = Column(Float, nullable=False) # TNF-alpha peak
    peak_il1b_pg_ml = Column(Float, nullable=False) # IL-1beta peak
    astct_crs_grade_predicted = Column(String(20), nullable=False) # Grade 0, Grade 1, Grade 2, Grade 3, Grade 4
    icans_neurotoxicity_risk_pct = Column(Float, nullable=False) # 0-100%
    tocilizumab_responsive = Column(Boolean, default=True)
    dexamethasone_recommended = Column(Boolean, default=False)
    safety_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    construct = relationship("DBCARTConstructDesign", back_populates="crs_profiles")
