# Agent & Developer Operating Instructions: AGENTS.md

Welcome to the **Agentic Multimodal Research Platform** codebase. This file serves as the definitive, tool-agnostic operational guide for human developers and autonomous AI coding agents working in this repository.

---

## 1. System Architecture & High-Level Philosophy

The repository is organized as a modular Python monorepo with a decoupled FastAPI backend and a React (TypeScript + Vite) frontend.

### The Core Vision: An AI Research Operating System
> **This isn't just a chatbot.**  
> The system enables AI to **Plan $\rightarrow$ Investigate $\rightarrow$ Retrieve $\rightarrow$ Reason $\rightarrow$ Critique $\rightarrow$ Synthesize $\rightarrow$ Report**, while managing multi-user authentication, quota allocation, multi-provider model routing, persistent storage, and real-time streaming progress.

### Architectural Tiers:
```
Frontend (React/Vite)
       │ HTTP / WebSocket
       ▼
FastAPI API Layer (apps/api)
       │
       ├── Auth & RBAC (JWT, PBKDF2, PostgreSQL/SQLite)
       ├── User Context Propagation (JWT User ID -> ResearchPipeline -> AgentContext)
       ├── Research Pipeline Orchestrator (packages/research)
       │      │
       │      ├── PlannerAgent (packages/agents)
       │      ├── Task DAG Execution Engine (packages/research)
       │      ├── Specialized Agents (Web, Document, Critic, Report)
       │      │      └── Tool Registry (packages/tools)
       │      └── Hybrid RAG Layer (packages/retrieval)
       │
       └── AI Engine (packages/ai)
              └── ModelGateway
                     └── ModelRouter
                            ├── ModelRegistry (Task capability matching & model definitions)
                            ├── ProviderRegistry (Ollama, Gemini, OpenAI-compatible)
                            └── Usage & Quotas (Row-locking concurrency, persistent tracking)
```

---

## 2. Tech Stack Overview

| Domain | Technology | Key Libraries / Protocols |
|---|---|---|
| **Backend Framework** | Python 3.11+ / FastAPI | Pydantic v2 Settings, Structlog, Uvicorn |
| **Database & ORM** | PostgreSQL 16 / SQLite parity | SQLAlchemy 2.0 Async, Alembic migrations |
| **Vector Search & RAG** | ChromaDB / In-Memory | `rank-bm25`, Reciprocal Rank Fusion (RRF) |
| **Multimodal Ingestion** | Custom pipeline | `pdfplumber`, `python-docx`, `Pillow`, Vision LLMs |
| **AI Providers** | Multi-provider Gateway | Local Ollama, Official Google Gemini, OpenAI-compatible |
| **Frontend Framework** | React 18 / TypeScript | Vite, React Router v6, Lucide React, Vanilla CSS |
| **Testing** | pytest & pytest-asyncio | `httpx`, pytest-cov |

---

## 3. Directory Layout

```
.
├── apps/
│   ├── api/                     # FastAPI backend application
│   │   ├── src/
│   │   │   ├── api/             # Routes (auth, research, documents, models, health, ws)
│   │   │   ├── dependencies.py  # Dependency injection (Gateway, Repositories, EventBus)
│   │   │   └── main.py          # Application entry & CORS/middleware
│   │   └── tests/               # API route integration tests
│   └── web/                     # React frontend
│       ├── src/
│       │   ├── components/      # UI components (Layout, Badges, Tables)
│       │   ├── pages/           # Dashboard, NewResearch, ResearchDetail, Settings
│       │   ├── services/        # api.ts (HTTP client) and WebSocket helpers
│       │   └── types/           # TypeScript types (ResearchJob, Task, Evidence, Report)
│       └── package.json
│
├── packages/                    # Core modular Python packages
│   ├── ai/                      # Multi-provider Gateway, Router, Registry, Quotas, Providers
│   ├── agents/                  # Autonomous agents (Planner, Web, Doc, Critic, Report)
│   ├── research/                # DAG execution, Pipeline, EventBus, Synthesis
│   ├── ingestion/               # Parsers (PDF, DOCX, Image, Text), Chunkers, Normalizers
│   ├── retrieval/               # Embedder, ChromaStore, InMemoryStore, BM25, Retriever
│   ├── database/                # SQLAlchemy async models, Repositories, Alembic
│   ├── tools/                   # Tool registry, WebSearch, SSRF-safe WebFetch, DocReader
│   └── shared/                  # Config, logging, JWT auth, security, exceptions
│
├── design/                      # UI/UX design specifications, tokens, and screens
├── docs/                        # Architectural specs, PRD, TRD, flows, schema, decisions
├── infrastructure/              # Kubernetes manifests, Docker Compose, monitoring
└── pyproject.toml               # Python monorepo configuration
```

---

## 4. Coding Conventions & Standards

### Python (Backend & Packages)
1. **Typing**: Use strict static typing across all packages (`typing.Optional`, `Union`, `List`, `Dict`, `Tuple`, or modern `|` syntax). Ensure all functions have parameter and return type hints.
2. **Pydantic**: Use Pydantic v2 schemas (`BaseModel`, `Field`, `model_dump()`, `model_copy()`).
3. **Async / Await**: All database interactions (`AsyncSession`), model inferences, HTTP queries (`httpx.AsyncClient`), and tool runs MUST be async. Never block the event loop.
4. **Error Handling**: Use domain exceptions defined in `shared.exceptions` (e.g., `ModelNotFoundError`, `ProviderUnavailableError`, `AuthenticationError`, `ValidationError`).
5. **Logging**: Always use structured logging with `structlog` (`logger = get_logger(__name__)`). Include contextual key-value pairs (e.g., `job_id`, `task_id`, `model`, `latency_ms`). Do not use `print()` in production packages.
6. **SQL Parity**: Database models must remain cross-compatible with PostgreSQL (using `JSONB` and native `UUID`) and SQLite (fallback variants via `JSON().with_variant(...)`).
7. **Deterministic Calculations**: AI agents must invoke deterministic Python tools for numerical, statistical, or mathematical evaluations rather than relying on LLMs to invent numbers.

### TypeScript / React (Frontend)
1. **Vanilla CSS**: Rely on the established design system tokens in `apps/web/src/index.css`. Avoid adding Tailwind CSS unless explicitly requested.
2. **State Management**: Keep components focused. Handle loading, error, and empty states explicitly.
3. **Resilient WebSockets**: Maintain exponential backoff auto-reconnect logic and support token authentication via query parameters or Authorization headers.

---

## 5. Development & Testing Commands

Run commands from the repository root or relevant project subdirectories:

```bash
# 1. Run all unit tests across all packages
pytest packages/ apps/api/tests/ -v

# 2. Run specific package tests
pytest packages/ai/tests/ -v
pytest packages/research/tests/ -v
pytest packages/ingestion/tests/ -v
pytest packages/database/tests/ -v

# 3. Apply database migrations
cd apps/api
alembic upgrade head

# 4. Start backend development server
uvicorn src.main:app --reload --port 8000

# 5. Build and validate frontend
cd apps/web
npm install
npm run build
npm run lint
```

---

## 6. Critical Constraints & Known Pitfalls

1. **Security & Secrets**: NEVER hardcode API keys, passwords, or JWT secrets in code or documentation. Always reference environment variables by name (e.g., `GEMINI_API_KEY`, `OPENAI_API_KEY`, `DATABASE_URL`, `SECRET_KEY`).
2. **SSRF Prevention**: When fetching web resources, always route through `WebFetchTool` or validate targets against `packages.shared.security.is_safe_url()`. Private IPs, loopbacks, and metadata service endpoints (e.g., `169.254.169.254`) must be rejected.
3. **Model Provider Architecture**: The legacy unofficial `GeminiWeb2API` scraper was completely removed in Phase 7.3. Use the official `ai.providers.gemini.GeminiProvider`. Do NOT restore or reintroduce Web2API scrapers.
4. **User Attribution Flow**: Always pass authenticated `user_id` down into `AgentContext` and `ModelGateway` so model usage records and quota limits are strictly attributed in `UsageRepository`.
5. **Quota Concurrency**: Quota verification utilizes transactional row locking (`SELECT ... FOR UPDATE` or equivalent SQLite locks) to prevent race conditions during concurrent requests.
6. **Anti-Patterns & Architectural Discipline ("What We Should NOT Do")**:
   - Do NOT add premature infrastructure (e.g., Kafka, Kubernetes distributed workers, 10 LLM providers, OAuth microservices, redundant vector databases).
   - Priority must remain: **Connect existing components and make the product genuinely useful before adding more infrastructure.**

---

## 7. Current Project Phase Status & Roadmap

### Completed Foundations:
- **Phase 1 (Foundation)**: 🟢 COMPLETE
- **Phase 2 (Research MVP)**: 🟢 COMPLETE
- **Phase 3 (Multimodal Ingestion)**: 🟢 COMPLETE
- **Phase 4 (Agentic System)**: 🟢 COMPLETE
- **Phase 5 (RAG / Knowledge Layer)**: 🟢 COMPLETE
- **Phase 6 (Production & Security)**: 🟢 COMPLETE
- **Phase 7 (Application Maturity)**: 🟢 COMPLETE (7.1 Dashboard fix, 7.2 Persistent DB users, 7.3 Official Gemini Provider, WebSockets, Auth completion)
- **Phase 8A (Intelligent Model Routing Core)**: 🟢 COMPLETE (`ModelRegistry`, `ModelRouter`, `ModelGateway` - Commit: `88ac57d`)
- **Phase 8B (Usage Tracking & Quotas)**: 🟢 COMPLETE (`UserQuota`, row-locking concurrency, quota-aware fallback - Commit: `a603114`)
- **Phase 9 (Intelligent Knowledge Automation)**: 🟢 COMPLETE (Zero-touch dual-indexing, status lifecycle, Planner KB integration, Hybrid DAG search)
- **Phase 10 (Evidence & Citation Intelligence)**: 🟢 COMPLETE (Fine-grained claim extraction, coordinate anchoring, contradiction detection, citation-grounded synthesis)
- **Phase 11 (Advanced Research Planning)**: 🟢 COMPLETE (Hierarchical query trees, ambiguity scoring, inferred scope resolution, dynamic agent capability routing, closed-loop replanning)
- **Phase 12 (Advanced Multimodal Research)**: 🟢 COMPLETE (Speech/audio transcription with timestamps, video timeline synchronization, scientific chart JSON data series parsing, multimodal chunking)
- **Phase 13 (Dataset & Data Analysis Intelligence)**: 🟢 COMPLETE (`TabularParser` CSV/TSV/Excel/JSON profiling, `DataAnalysisTool`, `DeterministicMathTool`, `DatasetViewer.tsx` UI)
- **Phase 14 (Document & Paper Intelligence)**: 🟢 COMPLETE (`AcademicPaperParser`, hierarchical section trees, BibTeX citation matching, `PaperAnalysisTool`, `MethodologyComparisonTool`, `PaperViewer.tsx` UI)
- **Phase 15 (Deep Research Engine)**: 🟢 COMPLETE (`DeepResearchEngine`, recursive hypothesis formulation, Critic gap audits, dynamic DAG subtask rescheduling, convergence guardrails $\tau \ge 0.85$, WebSocket iteration telemetry, `DeepResearchTracker.tsx` UI)
- **Phase 16 (Research Memory)**: 🟢 COMPLETE (`DBResearchMemory`, `MemoryRepository`, `ResearchMemoryManager`, auto-consolidation from reports, `RecallMemoryTool`, `StoreMemoryTool`, `/api/v1/memory` REST API, `ResearchMemoryViewer.tsx` & `MemoryPage.tsx` UI)
- **Phase 17 (Long-Term Knowledge Graph)**: 🟢 COMPLETE (`DBKnowledgeEntity`, `DBKnowledgeRelation`, `KnowledgeGraphRepository`, `KnowledgeGraphEngine`, GraphRAG, `QueryKnowledgeGraphTool`, `ExtractGraphTripletsTool`, `FindRelationPathTool`, `/api/v1/graph` REST API, `KnowledgeGraphViewer.tsx` & `KnowledgeGraphPage.tsx` UI)
- **Phase 18 (Projects & Workspaces)**: 🟢 COMPLETE (`DBWorkspace`, `DBWorkspaceMember`, `DBProject`, `WorkspaceRepository`, `ProjectRepository`, `/api/v1/workspaces` & `/api/v1/projects` REST APIs, `WorkspaceSelector.tsx` & `ProjectsPage.tsx` UI)
- **Phase 19 (Team Collaboration)**: 🟢 COMPLETE (`DBWorkspaceInvite`, `DBReportAnnotation`, `DBWorkspaceActivity`, `WorkspaceInviteRepository`, `ReportAnnotationRepository`, `WorkspaceActivityRepository`, `/api/v1/workspaces/{id}/invites`, `/api/v1/invites/{token}`, `/api/v1/reports/{id}/annotations`, `WorkspaceMembersModal.tsx`, `ReportAnnotationsDrawer.tsx` UI)
- **Phase 20 (Intelligent Model Ecosystem)**: 🟢 COMPLETE (`ModelEcosystemOptimizer`, Pareto-frontier sorting, multi-parameter scoring across Quality/Speed/Cost/Locality, `/api/v1/models/profiles`, `/api/v1/models/optimize`, live simulation preview UI)
- **Phase 21 (Model Evaluation System)**: 🟢 COMPLETE (`BenchmarkDataset`, `DEFAULT_RESEARCH_BENCHMARK`, `EvaluationMetricsEngine`, `ModelEvaluator`, `DBModelEvaluation`, `DBModelBenchmarkResult`, `ModelEvaluationRepository`, `/api/v1/models/evaluate`, `/api/v1/models/evaluations`, `/api/v1/models/leaderboard`, `ModelEvaluationPage.tsx` UI)
- **Phase 22 (Agent Evaluation)**: 🟢 COMPLETE (`AgentEvaluator`, `AgentEvaluationScorecard`, `AgentStepTelemetry`, plan precision, tool accuracy, evidence coverage, hallucination rate scoring, `DBAgentEvaluation`, `DBAgentStepMetric`, `AgentEvaluationRepository`, `/api/v1/agents/evaluate`, `/api/v1/agents/evaluations`, `/api/v1/agents/metrics/summary`, `AgentEvaluationPage.tsx` UI)
- **Phase 23 (Enterprise Security)**: 🟢 COMPLETE (`KMSEnvelopeEncryption` AES-256-GCM, `AuditHashChainer` Merkle/SHA-256 hash chains, `DBSecurityAuditLog`, `DBEncryptedSecret`, `DBSecurityPolicy`, `SecurityRepository`, GDPR cascade purge, SOC 2 scorecard API, `EnterpriseSecurityPage.tsx` UI)
- **Phase 24 (Production Infrastructure)**: 🟢 COMPLETE (`AsyncTaskQueue` priority engine, `WorkerNode` lifecycle tracking, `ObjectStorageClient` S3/MinIO/Local abstraction, `DBWorkerNode`, `DBStorageObject`, `InfrastructureRepository`, `/api/v1/system` REST APIs, `ProductionInfrastructurePage.tsx` UI)
- **Phase 25 (Public API & Developer Platform)**: 🟢 COMPLETE (`DBApiKey`, `ApiKeyRepository` SHA-256 keys, `/api/v1/developer/*` REST API, rate limit tiers, permission scopes, `DeveloperPlatformPage.tsx` UI)
- **Phase 26 (Research Automation)**: 🟢 COMPLETE (`DBScheduledResearch`, `DBResearchSweepResult`, `DBAutomationAlert`, `AutomationRepository`, `ResearchAutomationEngine`, cron & interval scheduling, novelty & diff scoring, multi-channel alerts, `/api/v1/automation/*` REST API, `ResearchAutomationPage.tsx` UI)
- **Phase 27 (Adversarial Multi-Agent Debate & Consensus Engine)**: 🟢 COMPLETE (`DBAgentDebate`, `DBDebateRound`, `DBDebateConsensus`, `DebateRepository`, `ProposerAgent`, `OpposerAgent`, `ConsensusArbiter`, `DebateEngine` with Elo updates, `/api/v1/debates/*` REST API, `DebateArenaPage.tsx` UI)
- **Phase 28 (Systematic Literature Review & Meta-Analysis Engine)**: 🟢 COMPLETE (`DBLiteratureReview`, `DBSLRCriterion`, `DBSLRStudyCandidate`, `DBMetaAnalysisReport`, `DBRiskOfBiasAssessment`, `LiteratureRepository`, `EffectSizeCalculator`, `HeterogeneityEngine`, `PooledEffectEstimator`, `PRISMAFlowTracker`, `/api/v1/literature/*` REST API, `LiteratureReviewPage.tsx` UI)
- **Phase 29 (In-Silico Experimentation & Computational Reproducibility Engine)**: 🟢 COMPLETE (`DBExperimentProtocol`, `DBReproducibilityRun`, `DBClaimVerificationTrace`, `ReproducibilityRepository`, `ReproducibilityEngine`, AST sandboxing, `/api/v1/reproducibility/*` REST API, `ReproducibilityPage.tsx` UI)
- **Phase 30 (Multimodal Scientific Presentation & Executive Podcasting Briefing Generator)**: 🟢 COMPLETE (`DBSynthesisPresentation`, `DBPresentationSlide`, `DBPodcastBriefing`, `PresentationRepository`, `PresentationGenerator`, `PodcastBriefingSynthesizer`, `/api/v1/presentations/*` REST API, `PresentationStudioPage.tsx` UI)
- **Documentation Architecture**: 🟢 COMPLETE (Stable branch: `develop/v1.1` — Generation 7 Complete & Active!)

