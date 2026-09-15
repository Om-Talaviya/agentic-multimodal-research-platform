"""Pydantic data models for the AI Research OS Python SDK."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ResearchJobCreateRequest(BaseModel):
    question: str
    objective: Optional[str] = None
    domain: str = "general"
    scope: str = "deep"
    project_id: Optional[str] = None
    timeout_seconds: int = 600


class TaskStatus(BaseModel):
    id: str
    description: str
    agent_type: str
    status: str
    dependencies: List[str] = Field(default_factory=list)
    output: Optional[Any] = None
    error: Optional[str] = None


class SynthesisReport(BaseModel):
    id: Optional[str] = None
    executive_summary: str = ""
    findings: List[Dict[str, Any]] = Field(default_factory=list)
    methodology: Dict[str, Any] = Field(default_factory=dict)
    conclusions: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    confidence_score: float = 0.0


class ResearchJobResponse(BaseModel):
    job_id: str
    request_id: str
    status: str
    question: str
    objective: Optional[str] = None
    domain: str = "general"
    scope: str = "deep"
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    tasks: List[TaskStatus] = Field(default_factory=list)
    report: Optional[SynthesisReport] = None
    poll_url: Optional[str] = None


class DocumentIngestResponse(BaseModel):
    document_id: str
    title: str
    filename: Optional[str] = None
    chunks_count: int = 0
    status: str = "ready"
    message: str = ""


class ApiUsageSummary(BaseModel):
    key_prefix: str
    rate_limit_tier: str
    rate_limit_rpm: int
    scopes: List[str] = Field(default_factory=list)
    total_requests: int = 0
    total_tokens_consumed: int = 0
    total_cost_usd: float = 0.0
