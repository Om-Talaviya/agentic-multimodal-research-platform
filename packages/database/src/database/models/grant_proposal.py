"""SQLAlchemy database models for Autonomous Scientific Grant & Research Proposal Synthesizer (Phase 35)."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON

from database.connection import Base
from database.models.memory import GUID

JSONType = JSON().with_variant(JSONB, "postgresql")


class DBGrantProposal(Base):
    """Represents an institutional scientific grant proposal project."""

    __tablename__ = "grant_proposals"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=True, index=True)
    workspace_id = Column(GUID(), nullable=True, index=True)
    project_id = Column(GUID(), nullable=True, index=True)
    research_job_id = Column(GUID(), nullable=True, index=True)

    title = Column(String(512), nullable=False)
    funding_agency = Column(String(128), default="NIH", nullable=False)  # NIH, NSF, HORIZON_EUROPE, DARPA, DOE
    grant_mechanism = Column(String(64), default="R01", nullable=False)  # R01, R21, CAREER, ERC_ADVANCED, BAA
    target_call_number = Column(String(128), nullable=True)

    project_duration_years = Column(Integer, default=5, nullable=False)
    total_requested_budget_usd = Column(Float, default=1500000.0, nullable=False)
    indirect_cost_rate_percent = Column(Float, default=52.0, nullable=False)

    status = Column(String(64), default="draft", nullable=False, index=True)  # draft, synthesizing, review_ready, submitted
    executive_abstract = Column(Text, nullable=True)
    significance_narrative = Column(Text, nullable=True)
    innovation_narrative = Column(Text, nullable=True)
    approach_narrative = Column(Text, nullable=True)
    preliminary_data_summary = Column(Text, nullable=True)

    mock_panel_overall_score = Column(Float, default=0.0, nullable=False)  # NIH scale: 10-90 or 1.0-9.0
    percentile_estimate = Column(Float, default=0.0, nullable=False)
    metadata_json = Column(JSONType, default=dict, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    aims = relationship("DBGrantSpecificAim", back_populates="proposal", cascade="all, delete-orphan", order_by="DBGrantSpecificAim.aim_number")
    budget_items = relationship("DBGrantBudgetItem", back_populates="proposal", cascade="all, delete-orphan", order_by="DBGrantBudgetItem.year_number")
    review_scorecards = relationship("DBGrantReviewScorecard", back_populates="proposal", cascade="all, delete-orphan", order_by="DBGrantReviewScorecard.created_at")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id) if self.user_id else None,
            "workspace_id": str(self.workspace_id) if self.workspace_id else None,
            "project_id": str(self.project_id) if self.project_id else None,
            "research_job_id": str(self.research_job_id) if self.research_job_id else None,
            "title": self.title,
            "funding_agency": self.funding_agency,
            "grant_mechanism": self.grant_mechanism,
            "target_call_number": self.target_call_number,
            "project_duration_years": self.project_duration_years,
            "total_requested_budget_usd": self.total_requested_budget_usd,
            "indirect_cost_rate_percent": self.indirect_cost_rate_percent,
            "status": self.status,
            "executive_abstract": self.executive_abstract,
            "significance_narrative": self.significance_narrative,
            "innovation_narrative": self.innovation_narrative,
            "approach_narrative": self.approach_narrative,
            "preliminary_data_summary": self.preliminary_data_summary,
            "mock_panel_overall_score": self.mock_panel_overall_score,
            "percentile_estimate": self.percentile_estimate,
            "metadata": self.metadata_json or {},
            "aims_count": len(self.aims) if "aims" in self.__dict__ and self.aims is not None else 0,
            "budget_items_count": len(self.budget_items) if "budget_items" in self.__dict__ and self.budget_items is not None else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class DBGrantSpecificAim(Base):
    """Represents a Specific Aim / Work Package in a scientific grant."""

    __tablename__ = "grant_specific_aims"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    proposal_id = Column(GUID(), ForeignKey("grant_proposals.id", ondelete="CASCADE"), nullable=False, index=True)

    aim_number = Column(Integer, default=1, nullable=False)
    title = Column(String(512), nullable=False)
    hypothesis = Column(Text, nullable=False)
    experimental_design = Column(Text, nullable=False)
    expected_outcomes = Column(Text, nullable=False)
    potential_pitfalls_and_alternatives = Column(Text, nullable=True)

    milestones_json = Column(JSONType, default=list, nullable=False)  # List of {quarter, milestone, deliverable}
    allocated_effort_percent = Column(Float, default=33.3, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    proposal = relationship("DBGrantProposal", back_populates="aims")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "proposal_id": str(self.proposal_id),
            "aim_number": self.aim_number,
            "title": self.title,
            "hypothesis": self.hypothesis,
            "experimental_design": self.experimental_design,
            "expected_outcomes": self.expected_outcomes,
            "potential_pitfalls_and_alternatives": self.potential_pitfalls_and_alternatives,
            "milestones": self.milestones_json or [],
            "allocated_effort_percent": self.allocated_effort_percent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DBGrantBudgetItem(Base):
    """Represents an itemized financial cost item in the grant budget."""

    __tablename__ = "grant_budget_items"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    proposal_id = Column(GUID(), ForeignKey("grant_proposals.id", ondelete="CASCADE"), nullable=False, index=True)

    year_number = Column(Integer, default=1, nullable=False)
    category = Column(String(64), default="personnel", nullable=False)  # personnel, equipment, compute_cloud, supplies, travel, publication
    item_name = Column(String(256), nullable=False)
    cost_usd = Column(Float, default=0.0, nullable=False)
    justification = Column(Text, nullable=False)
    is_direct_cost = Column(String(10), default="true", nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    proposal = relationship("DBGrantProposal", back_populates="budget_items")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "proposal_id": str(self.proposal_id),
            "year_number": self.year_number,
            "category": self.category,
            "item_name": self.item_name,
            "cost_usd": self.cost_usd,
            "justification": self.justification,
            "is_direct_cost": self.is_direct_cost == "true",
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DBGrantReviewScorecard(Base):
    """Represents an autonomous mock study section peer review evaluation of the grant proposal."""

    __tablename__ = "grant_review_scorecards"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    proposal_id = Column(GUID(), ForeignKey("grant_proposals.id", ondelete="CASCADE"), nullable=False, index=True)

    reviewer_persona = Column(String(64), default="study_section_chair", nullable=False)
    significance_score = Column(Float, default=2.0, nullable=False)  # 1.0 (exceptional) - 9.0 (poor)
    investigators_score = Column(Float, default=2.0, nullable=False)
    innovation_score = Column(Float, default=2.0, nullable=False)
    approach_score = Column(Float, default=2.0, nullable=False)
    environment_score = Column(Float, default=1.5, nullable=False)
    overall_impact_score = Column(Float, default=2.1, nullable=False)

    recommendation = Column(String(64), default="fundable", nullable=False)  # high_priority_fund, fundable, discuss_only, triaged
    critique_strengths = Column(JSONType, default=list, nullable=False)
    critique_weaknesses = Column(JSONType, default=list, nullable=False)
    summary_statement = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    proposal = relationship("DBGrantProposal", back_populates="review_scorecards")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "proposal_id": str(self.proposal_id),
            "reviewer_persona": self.reviewer_persona,
            "significance_score": self.significance_score,
            "investigators_score": self.investigators_score,
            "innovation_score": self.innovation_score,
            "approach_score": self.approach_score,
            "environment_score": self.environment_score,
            "overall_impact_score": self.overall_impact_score,
            "recommendation": self.recommendation,
            "critique_strengths": self.critique_strengths or [],
            "critique_weaknesses": self.critique_weaknesses or [],
            "summary_statement": self.summary_statement,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
