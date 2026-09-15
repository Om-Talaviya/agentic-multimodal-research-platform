"""Database models for Autonomous Drug Repurposing & Combination Synergy Simulator (Phase 45)."""
from datetime import datetime, timezone
import uuid
from typing import List, Optional, Dict, Any

from sqlalchemy import String, Float, Integer, ForeignKey, Text, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base
from database.models.memory import GUID, JSONType

class DBDrugRepurposingScreen(Base):
    __tablename__ = "drug_repurposing_screens"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id: Mapped[Optional[str]] = mapped_column(GUID(), ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True)
    project_id: Mapped[Optional[str]] = mapped_column(GUID(), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    disease_indication: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., Glioblastoma, Sorafenib-Resistant HCC
    screening_library: Mapped[str] = mapped_column(String(100), default="FDA-Approved & Phase III Clinical Library")
    
    total_screened: Mapped[int] = mapped_column(Integer, default=2450)
    top_candidates_count: Mapped[int] = mapped_column(Integer, default=5)
    status: Mapped[str] = mapped_column(String(50), default="completed")
    
    meta_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    candidates: Mapped[List["DBRepurposedCandidate"]] = relationship("DBRepurposedCandidate", back_populates="screen", cascade="all, delete-orphan")
    synergies: Mapped[List["DBDrugCombinationSynergy"]] = relationship("DBDrugCombinationSynergy", back_populates="screen", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_screen_disease", "disease_indication"),
    )

class DBRepurposedCandidate(Base):
    __tablename__ = "repurposed_candidates"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    screen_id: Mapped[str] = mapped_column(GUID(), ForeignKey("drug_repurposing_screens.id", ondelete="CASCADE"), nullable=False)
    
    drug_name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., Metformin, Disulfiram, Niclosamide
    original_indication: Mapped[str] = mapped_column(String(150), nullable=False)
    proposed_mechanism: Mapped[Text] = mapped_column(Text, nullable=False)
    
    connectivity_score: Mapped[float] = mapped_column(Float, nullable=False)  # -1.0 (strong reversal) to +1.0
    ic50_um: Mapped[float] = mapped_column(Float, default=1.85)  # micromolar potency
    clinical_safety_tier: Mapped[str] = mapped_column(String(50), default="High (FDA Approved)")
    evidence_publications_count: Mapped[int] = mapped_column(Integer, default=12)
    
    meta_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    screen: Mapped["DBDrugRepurposingScreen"] = relationship("DBDrugRepurposingScreen", back_populates="candidates")

    __table_args__ = (
        Index("ix_cand_screen", "screen_id"),
        Index("ix_cand_connectivity", "connectivity_score"),
    )

class DBDrugCombinationSynergy(Base):
    __tablename__ = "drug_combination_synergies"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    screen_id: Mapped[str] = mapped_column(GUID(), ForeignKey("drug_repurposing_screens.id", ondelete="CASCADE"), nullable=False)
    
    drug_a: Mapped[str] = mapped_column(String(100), nullable=False)
    drug_b: Mapped[str] = mapped_column(String(100), nullable=False)
    
    zip_synergy_score: Mapped[float] = mapped_column(Float, nullable=False)  # > 10.0 strong synergy, < -10 antagonism
    bliss_excess_score: Mapped[float] = mapped_column(Float, default=14.5)
    loewe_combination_index: Mapped[float] = mapped_column(Float, default=0.68)  # < 1.0 indicates synergy
    
    synergy_classification: Mapped[str] = mapped_column(String(50), default="Synergistic")  # Synergistic, Additive, Antagonistic
    dose_reduction_index: Mapped[float] = mapped_column(Float, default=3.8)  # 3.8x dose reduction possible
    ddi_toxicity_risk: Mapped[str] = mapped_column(String(50), default="Low")
    
    synergy_matrix_2d: Mapped[Optional[List[List[float]]]] = mapped_column(JSONType, nullable=True)
    meta_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    screen: Mapped["DBDrugRepurposingScreen"] = relationship("DBDrugRepurposingScreen", back_populates="synergies")

    __table_args__ = (
        Index("ix_synergy_screen", "screen_id"),
        Index("ix_synergy_zip", "zip_synergy_score"),
    )
