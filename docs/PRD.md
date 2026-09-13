# Product Requirements Document (PRD)

## Project: Agentic Multimodal Research Platform (AI Research OS)
**Status**: Active / Production v1.1 (Phase 17 Complete, Preparing Phase 18)  
**Author**: Engineering & AI Systems Team  
**Last Updated**: September 2026  
**Stable Branch**: `develop/v1.1`

---

## 1. Executive Summary & Vision

The **Agentic Multimodal Research Platform** is an enterprise-grade, local-first **AI Research Operating System**. It transforms ambiguous, complex research inquiries into structured, verified, and citation-backed intelligence reports with complete auditability, zero hallucinations, and strict data privacy.

### The Core Paradigm Shift
> **This isn't just a chatbot.**  
> Rather than a single prompt `Question $\rightarrow$ LLM $\rightarrow$ Answer`, the system executes an autonomous agentic pipeline:  
> **Plan $\rightarrow$ Investigate $\rightarrow$ Retrieve $\rightarrow$ Reason $\rightarrow$ Critique $\rightarrow$ Synthesize $\rightarrow$ Report**, while managing multi-user authentication, quota allocation, multi-provider model routing, persistent storage, and real-time streaming progress.

---

## 2. Problem Statement

Modern intelligence gathering, academic research, and technical analysis face four critical bottlenecks:
1. **Multimodal Data Fragmentation**: Information is trapped across disconnected sources—academic PDFs with embedded tables, scanned diagrams, intranet DOCX files, spreadsheets, and dynamic web pages.
2. **Hallucinations & Lack of Provenance**: Standard LLMs generate authoritative-sounding answers without verifiable source citations, page-level anchors, or confidence scoring.
3. **Monolithic Task Limits**: Complex research queries require strategic decomposition, parallel sub-investigations, iterative verification, and synthesis—capabilities that single-prompt models cannot achieve.
4. **Cloud Privacy & Vendor Lock-In**: Organizations hesitate to upload sensitive proprietary research to closed commercial AI clouds.

---

## 3. Target Users & Personas

- **Enterprise Researchers & Analysts**: Need deep literature synthesis across hundreds of pages of internal and external documentation with strict evidence mapping.
- **R&D Engineers & Scientists**: Require precise technical summaries with exact data extraction from PDF tables, mathematical formulas, and scientific preprints.
- **Academics & Graduate Students**: Require literature reviews comparing methodologies, identifying contradictions across papers, and generating verifiable citations.
- **Compliance & Legal Officers**: Require 100% provenance and citation tracking for every factual claim.
- **Self-Hosted / Privacy-Conscious Organizations**: Need the entire agentic pipeline to run offline or local-first using local hardware (Ollama) without data leakage.

---

## 4. Business & Quota Model

The platform includes persistent usage tracking and token/cost quota enforcement with three distinct service tiers:

| Tier | Research Jobs | Token / Cost Quotas | Knowledge Storage | Model Access | Collaboration |
|---|---|---|---|---|---|
| **FREE** | Limited concurrent jobs | Strict lifetime/monthly token limits | Limited document storage | Local / Standard Fast Models | Single User |
| **PRO** | High concurrent jobs | Expanded token & cost quotas | Large private knowledge base | Advanced Reasoning & Vision Models | Single User |
| **TEAM** | Unlimited concurrent jobs | Shared team quotas & cost centers | Shared organizational knowledge | All Catalog & Custom Models | Shared Workspaces, Roles & Versioning |

---

## 5. End-to-End User Experience

### 5.1 Platform Navigation & Dashboard
The UI provides a unified research workspace:
- **Dashboard**: Recent research jobs, execution states, quick research launcher.
- **Research**: Active investigations, live DAG visualization, real-time WebSocket logs.
- **Knowledge**: Private knowledge base, indexed document collections, chunk statistics.
- **Documents**: Upload hub for PDFs, DOCX, images, datasets (CSV, Excel).
- **Projects & Workspaces**: Structured project folders and team spaces (Generation 4).
- **Reports**: Finished intelligence reports with citation explorer and export options.
- **Memory**: Persistent cross-session research memory studio, conceptual indexing, tag filters.
- **Settings**: Model provider toggles, Ollama endpoints, API keys, quota monitors.

### 5.2 Research Execution Progression
When a user submits a query (e.g., *"Analyze whether biodegradable packaging can realistically replace conventional plastic in food packaging over the next 10 years"*), the system streams progress in real time:
1. `Understanding Request...`
2. `Recalling Cross-Session Research Memory...`
3. `Planning Research & Decomposing Subquestions...`
4. `Checking Private Knowledge Base...`
5. `Retrieving Relevant Document Context...`
6. `Conducting External Web Investigations...`
7. `Analyzing Academic Papers & Tables...`
8. `Analyzing Tabular Data & Statistics...`
9. `Comparing Evidence & Cross-Checking Claims...`
10. `Identifying Contradictions & Uncertainties...`
11. `Critic Review (Auditing Sufficiency & Hypothesis Testing)...`
12. `Iterative Deep Research Loop (if evidence gaps or hypotheses unverified)...`
13. `Synthesizing Final Intelligence Report...`
14. `Auto-Persisting Verified Findings to Research Memory...`
15. `Completed & Ready for Interactive Exploration.`

### 5.3 Final Report Experience & Explainability
The output is a structured intelligence dossier:
- **Executive Summary**: High-level overview of findings.
- **Research Question & Scope**: Precise parameters of the investigation.
- **Methodology**: Strategy, data sources queried, and agent workflows.
- **Key Findings**: Numbered, authoritative findings.
- **Evidence Matrix**: Detailed breakdown mapping every claim to exact sources (e.g., `Paper A - Page 12`, `Uploaded Doc B - Section 4.2`, `Web Source C`).
- **Contradictions & Uncertainty Analysis**: Explicit identification of conflicting data across sources.
- **Market & Technical Analysis**: In-depth evaluation of technological and economic viability.
- **Data Analysis & Visualizations**: Deterministically calculated statistics, tables, and charts.
- **Risks & Limitations**: Known unknowns, study limitations, and external risks.
- **Conclusion**: Actionable synthesis.
- **Confidence / Evidence Coverage Score**: Quantitative coverage metric (e.g., `82% Confidence`).
- **Explainability Anchor ("Why do you believe this?")**: Interactive provenance lookup:  
  `Answer $\rightarrow$ Reasoning/Evidence $\rightarrow$ Sources $\rightarrow$ Original Documents $\rightarrow$ Relevant Pages/Sections`.

---

## 6. Current Completed Scope (Phases 1 – 17)

- ✅ **Phase 1 (Foundation)**: Core monorepo structure, async FastAPI backend, SQLAlchemy async, React/Vite shell.
- ✅ **Phase 2 (Research MVP)**: DAG task scheduler, PlannerAgent, Web/Doc/Report agents, live WebSockets.
- ✅ **Phase 3 (Multimodal Ingestion)**: Native PDF parser (`pdfplumber` with table extraction), DOCX parser, image parser with vision LLMs, semantic chunker.
- ✅ **Phase 4 (Agentic System)**: SSRF-hardened `WebFetchTool`, independent `CriticAgent`, execution tracing.
- ✅ **Phase 5 (RAG / Knowledge Layer)**: Hybrid RRF retrieval combining ChromaDB/In-Memory vector search and BM25 sparse search.
- ✅ **Phase 6 (Production & Security)**: JWT access/refresh lifecycle, PBKDF2 password hashing, RBAC, Prometheus metrics (`/metrics`), Kubernetes manifests.
- ✅ **Phase 7 (Application Maturity)**:
  - 7.1 Dashboard UI data mapping fix.
  - 7.2 Persistent PostgreSQL `users` table with Alembic migrations.
  - 7.3 Official Google Gemini SDK migration & complete deletion of legacy Web2API scrapers.
  - Authenticated WebSocket streaming with snapshot hydration.
- ✅ **Phase 8A (Intelligent Model Routing Core)**: `ModelRegistry`, `ProviderRegistry`, `ModelRouter`, and `ModelGateway` with task matching and automated fallback failover (Commit: `88ac57d`).
- ✅ **Phase 8B (Usage Tracking & Quota Subsystem)**: Persistent `UsageRecord` and `UserQuota` models with transactional row-locking concurrency, quota-aware fallback, and pipeline user attribution (Commit: `a603114`).
- ✅ **Phase 9 (Intelligent Knowledge Automation)**: Automated end-to-end zero-touch ingestion and dual-indexing (`Upload $\rightarrow$ Validate $\rightarrow$ Extract $\rightarrow$ Chunk $\rightarrow$ Embed $\rightarrow$ Index`), document status lifecycle, and planner retrieval integration.
- ✅ **Phase 10 (Evidence & Citation Intelligence)**: Fine-grained claim extraction, paragraph/table coordinate anchoring (`CitationCoordinates`), pairwise contradiction detection taxonomy in `CriticAgent`, and citation-grounded report synthesis.
- ✅ **Phase 11 (Advanced Research Planning)**: Hierarchical query trees, ambiguity scoring, dynamic agent capability routing, closed-loop replanning.
- ✅ **Phase 12 (Advanced Multimodal Research)**: Unified synthesis across 50+ page PDFs, research papers, images, charts, audio/video transcripts with timestamp and coordinate grounding.
- ✅ **Phase 13 (Dataset & Data Analysis Intelligence)**: Schema inference and tabular profiling for CSV/TSV/Excel/JSON, deterministic calculation tools (`DataAnalysisTool`, `DeterministicMathTool`), and interactive data viewer.
- ✅ **Phase 14 (Document & Paper Intelligence)**: Academic paper parser (`AcademicPaperParser`), section tree hierarchies, BibTeX citation matching, `PaperAnalysisTool`, `MethodologyComparisonTool`.
- ✅ **Phase 15 (Deep Research Engine)**: Recursive hypothesis formulation, Critic gap audits, dynamic DAG subtask rescheduling, convergence guardrails $\tau \ge 0.85$, WebSocket iteration telemetry, and `DeepResearchTracker` UI.
- ✅ **Phase 16 (Research Memory)**: Persistent cross-session research memory (`DBResearchMemory`, `MemoryRepository`, `ResearchMemoryManager`), semantic conceptual indexing, agent memory tools (`RecallMemoryTool`, `StoreMemoryTool`), REST API (`/api/v1/memory`), and interactive `ResearchMemoryViewer` UI.
- ✅ **Phase 18 (Projects & Workspaces)**: Multi-tiered hierarchical resource scoping (`User -> Workspace -> Projects -> Research & Knowledge`), `DBWorkspace`, `DBWorkspaceMember`, `DBProject`, `WorkspaceRepository`, `ProjectRepository`, REST APIs (`/api/v1/workspaces`, `/api/v1/projects`), `WorkspaceContext`, and React UI studio.
- ✅ **Phase 19 (Team Collaboration)**: Granular workspace RBAC (`owner`, `admin`, `researcher`, `analyst`, `reviewer`, `viewer`), cryptographic email invitation lifecycle (`DBWorkspaceInvite`, `WorkspaceInviteRepository`), threaded report annotations with quotes and 1-click resolution (`DBReportAnnotation`, `ReportAnnotationsDrawer.tsx`), and collaborative audit activity logs (`DBWorkspaceActivity`).

---

## 7. 6-Generation Product Roadmap (Phases 9 – 26)

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                   AGENTIC MULTIMODAL RESEARCH PLATFORM ROADMAP                   │
└──────────────────────────────────────────────────────────────────────────────────┘
  Phase 1 to 14: Platform Foundation, Multimodal Intelligence & Paper Analysis [COMPLETE]
                             │
                             ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │ GENERATION 3: Autonomous Research                                            │
  │ • Phase 15: Deep Research Engine (Recursive Feedback Loops) [COMPLETE]       │
  │ • Phase 16: Research Memory (Cross-Session Project Memory)  [COMPLETE]       │
  │ • Phase 17: Long-Term Knowledge Graph (Entity-Relation Reasoning) [COMPLETE] │
  └──────────────────────────────────────┬───────────────────────────────────────┘
                                         ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │ GENERATION 4: Collaboration Platform                                         │
  │ • Phase 18: Projects & Workspaces Organization [COMPLETE]                    │
  │ • Phase 19: Team Collaboration (Roles, Invites, Report Annotations) [COMPLETE]│
  └──────────────────────────────────────┬───────────────────────────────────────┘
                                         ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │ GENERATION 5: AI Platform Intelligence                                       │
  │ • Phase 20: Intelligent Model Ecosystem (NEXT MILESTONE)                     │
  │ • Phase 21: Model Evaluation System (Automated Benchmarking)                 │
  │ • Phase 22: Agent Evaluation (Hallucination & Efficiency Observability)      │
  └──────────────────────────────────────┬───────────────────────────────────────┘
                                         ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │ GENERATION 6: Production Product                                             │
  │ • Phase 23: Enterprise Security (SOC 2, GDPR, Immutable Audit Logs)          │
  │ • Phase 24: Production Scale Infrastructure (Task Queues, Distributed Pool)  │
  │ • Phase 25: Public API & Developer Platform (SDKs, API Keys)                 │
  │ • Phase 26: Research Automation (Scheduled Sweeps, Real-Time Market Alerts)  │
  └──────────────────────────────────────┬───────────────────────────────────────┘
                                         ▼
                            [ AI RESEARCH OPERATING SYSTEM ]
```

### 7.1 Detailed Phase Breakdown

#### Generation 1 — Intelligent Research Core (COMPLETE)
- **Phase 9: Intelligent Knowledge Automation (COMPLETE)**:
  - Automated document pipeline: `Upload $\rightarrow$ Validate $\rightarrow$ Extract $\rightarrow$ Normalize $\rightarrow$ Chunk $\rightarrow$ Embed $\rightarrow$ Index $\rightarrow$ Ready`.
  - Planner awareness: Planner evaluates whether user documents contain relevant context before scheduling external searches.
- **Phase 10: Evidence & Citation Intelligence (COMPLETE)**:
  - Fine-grained claim extraction and source linking with page/paragraph coordinates.
  - Source reliability scoring, contradictory claim detection, and citation-aware report generation.
- **Phase 11: Advanced Research Planning (COMPLETE)**:
  - Complex problem decomposition into hierarchical query trees, identifying evidence prerequisites, selecting research methods, assigning specialized agent roles, and closed-loop replanning.

#### Generation 2 — Multimodal Intelligence (COMPLETE)
- **Phase 12: Advanced Multimodal Research (COMPLETE)**:
  - Unified synthesis across 50+ page PDFs, research papers, images, charts, graphs, tables, audio recordings, and video transcripts with timestamp and coordinate grounding.
- **Phase 13: Dataset & Data Analysis Intelligence (COMPLETE)**:
  - Schema inference and analysis for CSV, TSV, Excel, and JSON data.
  - Integration of deterministic Python computation tools for statistics (mean, correlation, regression) and visualization enforcing **ADR 007** and **ADR 013** zero-hallucination standards.
- **Phase 14: Document & Paper Intelligence (COMPLETE)**:
  - Deep semantic parsing of academic literature (`AcademicPaperParser`), section tree hierarchies (`PaperSection`), BibTeX citation matching, and automated cross-paper methodology comparisons (**ADR 014**).

#### Generation 3 — Autonomous Research (COMPLETE)
- **Phase 15: Deep Research Engine (COMPLETE)**:
  - Recursive execution loops: When `CriticAgent` detects insufficient evidence or unresolved questions, the `PlannerAgent` dynamically schedules follow-up investigation tasks.
- **Phase 16: Research Memory (COMPLETE)**:
  - Persistent research memory indexing past papers, queries, findings, and hypotheses across sessions. Enables agents to recall prior discoveries and prevent duplicate work (**ADR 016**).
- **Phase 17: Long-Term Knowledge Graph (COMPLETE)**:
  - Structured graph representation of entities, authors, technologies, companies, claims, and datasets for graph-augmented reasoning (**ADR 017**).

#### Generation 4 — Collaboration Platform (COMPLETE)
- **Phase 18: Projects & Workspaces (COMPLETE)**:
  - Hierarchical workspace hierarchy: `User $\rightarrow$ Workspace $\rightarrow$ Projects $\rightarrow$ Research & Knowledge` (**ADR 018**).
- **Phase 19: Team Collaboration (COMPLETE)**:
  - Granular team roles (Owner, Researcher, Analyst, Reviewer, Viewer), workspace invitations, shared project knowledge, inline report annotations, and collaborative audit activity logs (**ADR 019**).

#### Generation 5 — AI Platform Intelligence
- **Phase 20: Intelligent Model Ecosystem (NEXT MILESTONE)**:
  - Multi-variable routing optimization factoring in task complexity, latency SLA, cost budget, context window, vision requirement, provider health, and user quota.
  - Multi-variable routing optimization factoring in task complexity, latency SLA, cost budget, context window, vision requirement, provider health, and user quota.
- **Phase 21: Model Evaluation System**:
  - Automated continuous evaluation of model outputs for accuracy, relevance, citation precision, and cost-efficiency.
- **Phase 22: Agent Evaluation**:
  - Observability dashboard tracking agent reasoning quality, hallucination rates, token efficiency, and execution durations.

#### Generation 6 — Production Product
- **Phase 23: Enterprise Security**:
  - Enterprise compliance (SOC 2, GDPR), encryption at rest and in transit, secret management, immutable audit logs, and data retention policies.
- **Phase 24: Production Scale Infrastructure**:
  - Distributed background task queues (Celery/Redis/RabbitMQ), worker autoscaling, S3/MinIO object storage, and PostgreSQL replication.
- **Phase 25: Public API & Developer Platform**:
  - Public developer REST API, API key provisioning, rate limiting, and official Python/TypeScript SDKs.
- **Phase 26: Research Automation**:
  - Cron-based recurring research jobs, automated change detection across academic archives and web sources, and notification dispatchers.

---

## 8. Architectural Anti-Patterns ("What We Should NOT Do")

To maintain momentum and high engineering quality, the following anti-patterns are strictly avoided:
1. **No Premature Infrastructure Bloat**: Do NOT introduce Kafka, Kubernetes distributed workers, 10 LLM providers, OAuth microservices, or redundant vector databases before the core agentic research loops are connected and useful.
2. **No Monolithic LLM Prompts**: Never replace multi-agent DAG decomposition with a single massive LLM prompt.
3. **No Hallucinated Calculations**: Never ask LLMs to perform arithmetic or statistical calculations directly; always delegate to deterministic tools.
4. **Core Philosophy**: **Make the research engine excellent first $\rightarrow$ make knowledge deeply integrated $\rightarrow$ make evidence trustworthy $\rightarrow$ make multimodal analysis powerful $\rightarrow$ make it collaborative $\rightarrow$ make it production-grade.**
