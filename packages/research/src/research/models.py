"""Research pipeline data models."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4
from shared.types import UUIDStr, TaskStatus, JobStatus


def utc_now() -> datetime:
    return datetime.now(UTC)


class ResearchRequest(BaseModel):
    question: str = Field(..., min_length=10, max_length=5000)
    context: Optional[str] = Field(None, max_length=10000)
    constraints: List[str] = Field(default_factory=list, max_length=20)
    preferred_sources: List[str] = Field(default_factory=list, max_length=10)
    user_id: Optional[str] = None


class ResearchJob(BaseModel):
    id: UUIDStr = Field(default_factory=lambda: str(uuid4()))
    request_id: UUIDStr = Field(default_factory=lambda: str(uuid4()))
    user_id: Optional[str] = None
    question: str
    objective: str
    domain: Optional[str] = None
    scope: Optional[str] = None
    constraints: List[str] = Field(default_factory=list)
    expected_output: str = "report"
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class ResearchTask(BaseModel):
    id: UUIDStr = Field(default_factory=lambda: str(uuid4()))
    job_id: UUIDStr
    type: str
    objective: str
    context: Dict[str, Any] = Field(default_factory=dict)
    agent: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    depends_on: List[str] = Field(default_factory=list)
    priority: int = 1
    status: TaskStatus = TaskStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None


class ResearchStep(BaseModel):
    id: str
    name: str
    description: str
    agent: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    depends_on: List[str] = Field(default_factory=list)
    priority: int = 1


class ResearchPlan(BaseModel):
    objective: str
    steps: List[ResearchStep] = Field(default_factory=list)
    expected_outputs: List[str] = Field(default_factory=list)


class CitationCoordinates(BaseModel):
    """Fine-grained physical coordinate anchors for grounding factual claims."""
    page_number: Optional[int] = None
    paragraph_index: Optional[int] = None
    table_row: Optional[int] = None
    table_col: Optional[int] = None
    char_start: Optional[int] = None
    char_end: Optional[int] = None


class Citation(BaseModel):
    """Structured verifiable citation mapping a claim to its exact source and coordinates."""
    id: UUIDStr = Field(default_factory=lambda: str(uuid4()))
    claim: str
    source_id: Optional[UUIDStr] = None
    document_id: Optional[str] = None
    citation_text: str = ""
    quote: str = ""
    coordinates: Optional[CitationCoordinates] = None
    confidence: float = 0.85
    source_reliability: float = 1.0


class Contradiction(BaseModel):
    """Detected conflict or discrepancy between two sources or claims."""
    id: UUIDStr = Field(default_factory=lambda: str(uuid4()))
    topic: str
    claim_a: str
    source_a: str
    claim_b: str
    source_b: str
    conflict_type: str = "direct_conflict"  # direct_conflict, numerical_discrepancy, methodological_divergence
    explanation: str
    severity: str = "medium"  # low, medium, high


class Source(BaseModel):
    id: UUIDStr = Field(default_factory=lambda: str(uuid4()))
    type: str
    url: Optional[str] = None
    title: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    content_hash: Optional[str] = None
    retrieved_at: datetime = Field(default_factory=utc_now)


class Evidence(BaseModel):
    id: UUIDStr = Field(default_factory=lambda: str(uuid4()))
    source_id: UUIDStr
    claim: str
    supporting_text: str
    confidence: float = 0.5
    verification_status: str = "unverified"
    verification_notes: Optional[str] = None
    citations: List[Citation] = Field(default_factory=list)
    coordinates: Optional[CitationCoordinates] = None


class Finding(BaseModel):
    id: UUIDStr = Field(default_factory=lambda: str(uuid4()))
    topic: str
    summary: str
    evidence_ids: List[UUIDStr] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)
    confidence: float = 0.7
    uncertainty: Optional[str] = None
    assumptions: List[str] = Field(default_factory=list)


class ResearchReport(BaseModel):
    id: UUIDStr = Field(default_factory=lambda: str(uuid4()))
    job_id: UUIDStr
    title: str
    executive_summary: str
    methodology: str
    findings: List[Finding] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)
    sources: List[Source] = Field(default_factory=list)
    contradictions: List[Contradiction] = Field(default_factory=list)
    confidence_score: float = 0.85
    conclusions: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=utc_now)
