"""Database models for Autonomous Systematic Literature Review (SLR) and PRISMA Meta-Analysis."""

from datetime import datetime, timezone
from typing import Optional, List
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    DateTime,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON

from database.connection import Base
from database.models.memory import GUID

JSONType = JSON().with_variant(JSONB, "postgresql")


class DBLiteratureReview(Base):
    """Represents a Systematic Literature Review project following PRISMA 2020 protocols."""

    __tablename__ = "literature_reviews"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    workspace_id = Column(
        GUID(),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    project_id = Column(
        GUID(),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    title = Column(String(500), nullable=False)
    research_question = Column(Text, nullable=False)
    protocol_type = Column(String(100), nullable=False, default="PRISMA-2020")
    
    # Current stage in PRISMA flow: identification, screening, eligibility, included, completed
    current_phase = Column(
        String(50),
        nullable=False,
        default="identification",
        index=True,
    )

    pico_framework = Column(JSONType, nullable=False, default=dict)  # {population, intervention, comparator, outcome}
    search_strategy = Column(JSONType, nullable=False, default=dict)  # {keywords, databases, date_range, boolean_query}
    
    total_identified = Column(Integer, nullable=False, default=0)
    total_screened = Column(Integer, nullable=False, default=0)
    total_eligible = Column(Integer, nullable=False, default=0)
    total_included = Column(Integer, nullable=False, default=0)
    total_excluded = Column(Integer, nullable=False, default=0)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    criteria = relationship(
        "DBSLRCriterion",
        back_populates="review",
        cascade="all, delete-orphan",
        order_by="DBSLRCriterion.order_index.asc()",
    )
    candidates = relationship(
        "DBSLRStudyCandidate",
        back_populates="review",
        cascade="all, delete-orphan",
        order_by="DBSLRStudyCandidate.created_at.desc()",
    )
    meta_analyses = relationship(
        "DBMetaAnalysisReport",
        back_populates="review",
        cascade="all, delete-orphan",
        order_by="DBMetaAnalysisReport.created_at.desc()",
    )


class DBSLRCriterion(Base):
    """Represents an Inclusion or Exclusion criterion for study screening."""

    __tablename__ = "slr_criteria"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    review_id = Column(
        GUID(),
        ForeignKey("literature_reviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    criterion_type = Column(String(20), nullable=False)  # 'inclusion' or 'exclusion'
    category = Column(String(100), nullable=False, default="general")  # 'study_design', 'population', 'methodology', 'date'
    description = Column(Text, nullable=False)
    order_index = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    review = relationship("DBLiteratureReview", back_populates="criteria")


class DBSLRStudyCandidate(Base):
    """Represents a screened candidate paper or study in an SLR pipeline."""

    __tablename__ = "slr_study_candidates"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    review_id = Column(
        GUID(),
        ForeignKey("literature_reviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title = Column(String(500), nullable=False)
    authors = Column(JSONType, nullable=False, default=list)
    publication_year = Column(Integer, nullable=True)
    venue = Column(String(300), nullable=True)
    doi = Column(String(200), nullable=True)
    url = Column(String(1000), nullable=True)
    abstract = Column(Text, nullable=True)

    # Screening triage status: identified, title_abstract_screened, full_text_screened, included, excluded
    screening_status = Column(
        String(50),
        nullable=False,
        default="identified",
        index=True,
    )

    exclusion_reason = Column(String(300), nullable=True)
    relevance_score = Column(Float, nullable=False, default=0.0)
    methodology_type = Column(String(100), nullable=True)  # RCT, Observational, Meta-Analysis, Benchmark, Case Study

    # Extracted quantitative data for meta-analysis if included
    sample_size = Column(Integer, nullable=True)
    effect_size = Column(Float, nullable=True)
    variance = Column(Float, nullable=True)
    standard_error = Column(Float, nullable=True)
    confidence_interval_low = Column(Float, nullable=True)
    confidence_interval_high = Column(Float, nullable=True)
    metric_name = Column(String(100), nullable=True)

    metadata_json = Column(JSONType, nullable=False, default=dict)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    review = relationship("DBLiteratureReview", back_populates="candidates")
    risk_of_bias = relationship(
        "DBRiskOfBiasAssessment",
        back_populates="candidate",
        uselist=False,
        cascade="all, delete-orphan",
    )


class DBRiskOfBiasAssessment(Base):
    """Represents a structured Risk of Bias (RoB) assessment for an included study."""

    __tablename__ = "slr_risk_of_bias"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(
        GUID(),
        ForeignKey("slr_study_candidates.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Domains: low_risk, some_concerns, high_risk
    selection_bias = Column(String(30), nullable=False, default="low_risk")
    confounding_bias = Column(String(30), nullable=False, default="low_risk")
    measurement_bias = Column(String(30), nullable=False, default="low_risk")
    reporting_bias = Column(String(30), nullable=False, default="low_risk")
    overall_risk = Column(String(30), nullable=False, default="low_risk")

    justification_notes = Column(Text, nullable=True)
    evaluated_by = Column(String(100), nullable=False, default="auto_arbiter")
    domain_scores = Column(JSONType, nullable=False, default=dict)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    candidate = relationship("DBSLRStudyCandidate", back_populates="risk_of_bias")


class DBMetaAnalysisReport(Base):
    """Represents a quantitative meta-analysis statistical synthesis across included studies."""

    __tablename__ = "slr_meta_analyses"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    review_id = Column(
        GUID(),
        ForeignKey("literature_reviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    synthesis_name = Column(String(300), nullable=False)
    effect_metric = Column(String(50), nullable=False, default="hedges_g")  # hedges_g, cohens_d, odds_ratio, risk_ratio
    model_type = Column(String(50), nullable=False, default="random_effects")  # fixed_effect, random_effects

    total_studies_analyzed = Column(Integer, nullable=False, default=0)
    pooled_effect_size = Column(Float, nullable=False, default=0.0)
    pooled_ci_lower = Column(Float, nullable=False, default=0.0)
    pooled_ci_upper = Column(Float, nullable=False, default=0.0)
    pooled_p_value = Column(Float, nullable=False, default=0.0)
    z_score = Column(Float, nullable=False, default=0.0)

    # Heterogeneity statistics
    q_statistic = Column(Float, nullable=False, default=0.0)
    degrees_of_freedom = Column(Integer, nullable=False, default=0)
    i_squared = Column(Float, nullable=False, default=0.0)  # Inconsistency percentage 0 - 100%
    tau_squared = Column(Float, nullable=False, default=0.0)  # Between-study variance

    forest_plot_data = Column(JSONType, nullable=False, default=list)
    subgroup_analyses = Column(JSONType, nullable=False, default=dict)
    summary_markdown = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    review = relationship("DBLiteratureReview", back_populates="meta_analyses")
