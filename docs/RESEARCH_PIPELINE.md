# Research Pipeline

## Overview

The research pipeline orchestrates the end-to-end process from user request to final report, coordinating multiple agents and maintaining full provenance.

## Pipeline Stages

```
Request → Analysis → Planning → Execution → Verification → Synthesis → Report
```

### 1. Request Analysis

```python
# packages/research/analysis.py
from packages.research.models import ResearchRequest, ResearchJob
from packages.ai.providers.router import ModelRouter
from packages.ai.schemas import ModelCapabilities, LLMRequest, LLMMessage

class RequestAnalyzer:
    """Analyzes and enriches research requests."""
    
    def __init__(self, router: ModelRouter):
        self.router = router
    
    async def analyze(self, request: ResearchRequest) -> ResearchJob:
        llm = self.router.select_llm(ModelCapabilities.for_task("planning"))
        
        # Enhance request with structured understanding
        response = await llm.complete(LLMRequest(
            messages=[
                LLMMessage(role="system", content="Analyze this research request. Identify: domain, scope, constraints, expected output type, key entities, suggested sources."),
                LLMMessage(role="user", content=request.question),
            ],
            temperature=0.3,
            json_mode=True,
        ))
        
        import json
        analysis = json.loads(response.content)
        
        return ResearchJob(
            id=str(uuid.uuid4()),
            question=request.question,
            objective=analysis.get("objective", request.question),
            domain=analysis.get("domain"),
            scope=analysis.get("scope"),
            constraints=analysis.get("constraints", []),
            expected_output=analysis.get("expected_output", "report"),
            status="pending",
        )
```

### 2. Planning

```python
# packages/research/planner.py
from packages.research.models import ResearchJob, ResearchPlan, ResearchStep
from packages.agents.planner.planner_agent import PlannerAgent
from packages.agents.base import AgentContext

class ResearchPlanner:
    """Creates execution plans from research jobs."""
    
    def __init__(self, planner_agent: PlannerAgent):
        self.planner = planner_agent
    
    async def create_plan(self, job: ResearchJob, context: AgentContext) -> ResearchPlan:
        task = ResearchTask(
            id=str(uuid.uuid4()),
            job_id=job.id,
            type="planning",
            objective=job.objective,
            context={
                "domain": job.domain,
                "scope": job.scope,
                "constraints": job.constraints,
            },
        )
        
        result = await self.planner.run(task, context)
        if not result.success:
            raise PlanningError(f"Planning failed: {result.errors}")
        
        return result.output
```

### 3. Task Execution

```python
# packages/research/executor.py
from packages.research.models import ResearchJob, ResearchPlan, ResearchTask, TaskStatus
from packages.agents.orchestrator import AgentOrchestrator
from packages.agents.registry import AgentRegistry
from packages.database.repositories import TaskRepository
import asyncio

class TaskExecutor:
    """Executes research plan tasks."""
    
    def __init__(
        self,
        orchestrator: AgentOrchestrator,
        agent_registry: AgentRegistry,
        task_repo: TaskRepository,
    ):
        self.orchestrator = orchestrator
        self.registry = agent_registry
        self.task_repo = task_repo
    
    async def execute_plan(self, job: ResearchJob, plan: ResearchPlan) -> None:
        # Build task DAG
        tasks = {step.id: step for step in plan.steps}
        completed = set()
        
        while len(completed) < len(tasks):
            # Find ready tasks (dependencies met)
            ready = [
                step for step in tasks.values()
                if step.id not in completed
                and all(dep in completed for dep in step.depends_on)
            ]
            
            if not ready:
                raise CircularDependencyError("Circular dependency in plan")
            
            # Execute ready tasks in parallel
            contexts = [
                self.orchestrator.create_context(job.id, step.id, job.request_id)
                for step in ready
            ]
            
            agent_tasks = [(step.agent, step) for step in ready]
            results = await self.orchestrator.run_parallel(agent_tasks, contexts[0])
            
            # Process results
            for step, result in zip(ready, results):
                if isinstance(result, Exception):
                    await self.task_repo.update_status(step.id, TaskStatus.FAILED, str(result))
                else:
                    await self.task_repo.update_status(step.id, TaskStatus.COMPLETED)
                    await self._store_results(step, result)
                
                completed.add(step.id)
```

### 4. Evidence Verification

```python
# packages/research/verification.py
from packages.research.models import Evidence, Source
from packages.ai.providers.router import ModelRouter
from packages.ai.schemas import ModelCapabilities, LLMRequest, LLMMessage

class EvidenceVerifier:
    """Verifies and cross-checks evidence."""
    
    def __init__(self, router: ModelRouter):
        self.router = router
    
    async def verify(self, evidence: list[Evidence], sources: list[Source]) -> list[Evidence]:
        """Cross-reference evidence across sources."""
        llm = self.router.select_llm(ModelCapabilities.for_task("research"))
        
        # Group evidence by claim similarity
        claim_groups = self._group_by_claim(evidence)
        
        verified = []
        for group in claim_groups:
            if len(group) == 1:
                # Single source - lower confidence
                e = group[0]
                e.verification_status = "single_source"
                e.confidence *= 0.8
                verified.append(e)
            else:
                # Multiple sources - check consensus
                verification = await self._check_consensus(group, llm)
                for e in group:
                    e.verification_status = verification.status
                    e.confidence = verification.adjusted_confidence
                    e.verification_notes = verification.notes
                    verified.append(e)
        
        return verified
    
    async def _check_consensus(self, evidence_group: list[Evidence], llm) -> "VerificationResult":
        claims_text = "\n".join([f"- {e.claim} (source: {e.source_id}, conf: {e.confidence})" for e in evidence_group])
        
        response = await llm.complete(LLMRequest(
            messages=[
                LLMMessage(role="system", content="Analyze these claims from different sources. Do they agree, conflict, or partially agree? Return JSON: {status: 'consensus'|'conflict'|'partial', adjusted_confidence: float, notes: string}"),
                LLMMessage(role="user", content=claims_text),
            ],
            temperature=0.2,
            json_mode=True,
        ))
        
        import json
        return VerificationResult(**json.loads(response.content))
```

### 5. Synthesis

```python
# packages/research/synthesis.py
from packages.research.models import Evidence, Finding, ResearchJob
from packages.ai.providers.router import ModelRouter
from packages.ai.schemas import ModelCapabilities, LLMRequest, LLMMessage
from packages.agents.synthesis.synthesis_agent import SynthesisAgent

class ResearchSynthesizer:
    """Synthesizes verified evidence into findings."""
    
    def __init__(self, synthesis_agent: SynthesisAgent):
        self.agent = synthesis_agent
    
    async def synthesize(self, job: ResearchJob, evidence: list[Evidence]) -> list[Finding]:
        # Group evidence by topic
        topics = self._cluster_evidence(evidence)
        
        findings = []
        for topic, topic_evidence in topics.items():
            task = ResearchTask(
                id=str(uuid.uuid4()),
                job_id=job.id,
                type="synthesis",
                objective=f"Synthesize findings on: {topic}",
                context={"evidence": [e.model_dump() for e in topic_evidence]},
            )
            
            # Create context for agent
            context = AgentContext(...)
            result = await self.agent.run(task, context)
            
            if result.success:
                findings.extend(result.output)
        
        return findings
```

### 6. Report Generation

```python
# packages/research/report.py
from packages.research.models import ResearchJob, Finding, ResearchReport
from packages.agents.report.report_agent import ReportAgent
from packages.agents.base import AgentContext

class ReportGenerator:
    """Generates final research reports."""
    
    def __init__(self, report_agent: ReportAgent):
        self.agent = report_agent
    
    async def generate(self, job: ResearchJob, findings: list[Finding], evidence: list[Evidence]) -> ResearchReport:
        task = ResearchTask(
            id=str(uuid.uuid4()),
            job_id=job.id,
            type="report",
            objective="Generate final research report",
            context={
                "question": job.question,
                "findings": [f.model_dump() for f in findings],
                "evidence_summary": self._summarize_evidence(evidence),
            },
        )
        
        context = AgentContext(...)
        result = await self.agent.run(task, context)
        
        if not result.success:
            raise ReportGenerationError(result.errors)
        
        return result.output
```

## Data Models

```python
# packages/research/models.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ResearchRequest(BaseModel):
    question: str
    context: Optional[str] = None
    constraints: List[str] = []
    preferred_sources: List[str] = []

class ResearchJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str
    question: str
    objective: str
    domain: Optional[str] = None
    scope: Optional[str] = None
    constraints: List[str] = []
    expected_output: str = "report"
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

class ResearchTask(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str
    type: str
    objective: str
    context: Dict[str, Any] = {}
    agent: str
    inputs: Dict[str, Any] = {}
    depends_on: List[str] = []
    priority: int = 1
    status: TaskStatus = TaskStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

class ResearchPlan(BaseModel):
    objective: str
    steps: List[ResearchStep] = []
    expected_outputs: List[str] = []

class ResearchStep(BaseModel):
    id: str
    name: str
    description: str
    agent: str
    inputs: Dict[str, Any] = {}
    depends_on: List[str] = []
    priority: int = 1

class Source(BaseModel):
    id: str
    type: str  # web, document, pdf, image, database
    url: Optional[str] = None
    title: str
    metadata: Dict[str, Any] = {}
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)

class Evidence(BaseModel):
    id: str
    source_id: str
    claim: str
    supporting_text: str
    confidence: float = 0.5
    verification_status: str = "unverified"  # unverified, single_source, consensus, conflict
    verification_notes: Optional[str] = None

class Finding(BaseModel):
    id: str
    topic: str
    summary: str
    evidence_ids: List[str] = []
    confidence: float
    uncertainty: Optional[str] = None
    assumptions: List[str] = []

class ResearchReport(BaseModel):
    id: str
    job_id: str
    title: str
    executive_summary: str
    methodology: str
    findings: List[Finding] = []
    evidence: List[Evidence] = []
    sources: List[Source] = []
    conclusions: List[str] = []
    limitations: List[str] = []
    generated_at: datetime = Field(default_factory=datetime.utcnow)
```

## Provenance Tracking

Every piece of evidence maintains full traceability:

```
ResearchReport
    ├── Finding
    │   └── evidence_ids → Evidence[]
    │       └── source_id → Source
    │           └── url / document_id / etc.
    │
    └── AgentTrace[] (full execution history)
```

This enables:
- Citation generation in reports
- Verification of any claim
- Debugging unexpected results
- Audit trails

---

*Pipeline designed for observability - every stage emits structured events for tracing.*