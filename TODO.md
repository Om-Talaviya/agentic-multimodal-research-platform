# Project Tasks & Roadmap: TODO.md

This document tracks all completed engineering milestones, the immediate active sprint, and the long-term backlog for the **Agentic Multimodal Research Platform (AI Research OS)**.

---

## 🟢 Completed Milestones (Phases 1 – 8B)

- [x] **Phase 1: Foundation**
  - [x] Modular Python monorepo setup (`packages/` + `apps/`).
  - [x] FastAPI asynchronous backend shell with logging.
  - [x] Database abstraction layer with SQLAlchemy 2.0 Async (PostgreSQL + SQLite).
  - [x] React 18 + TypeScript + Vite frontend application.
- [x] **Phase 2: Research MVP**
  - [x] Directed Acyclic Graph (DAG) task scheduler and execution engine.
  - [x] Autonomous `PlannerAgent`, `WebResearchAgent`, `DocumentAnalysisAgent`, `ReportAgent`.
  - [x] Real-time WebSocket event streaming.
- [x] **Phase 3: Multimodal Ingestion Pipeline**
  - [x] Native PDF parsing with tabular grid extraction (`pdfplumber`).
  - [x] Word document extraction (`python-docx`).
  - [x] Image visual extraction via Vision LLMs (`Pillow`).
  - [x] Semantic boundary chunking with metadata preservation.
- [x] **Phase 4: Agentic System Core**
  - [x] SSRF-hardened `WebFetchTool` with private IP and loopback blocking.
  - [x] Independent `CriticAgent` with claim confidence scoring and contradiction detection.
  - [x] Agent execution tracing and error recovery.
- [x] **Phase 5: Hybrid RAG & Knowledge Layer**
  - [x] Dense vector search (ChromaDB + In-Memory store).
  - [x] Sparse keyword search (`rank-bm25`).
  - [x] Reciprocal Rank Fusion (RRF) hybrid context ranking.
- [x] **Phase 6: Production & Security**
  - [x] JWT access & refresh token lifecycle, PBKDF2 password hashing.
  - [x] Role-Based Access Control (`Admin`, `Researcher`, `Viewer`).
  - [x] Prometheus `/metrics` exposition and Kubernetes deployment manifests.
- [x] **Phase 7: Application Maturity**
  - [x] Phase 7.1: Dashboard UI data mapping fix.
  - [x] Phase 7.2: Persistent PostgreSQL `users` table with Alembic migrations.
  - [x] Phase 7.3: Migration to official Google Gemini SDK (`ai.providers.gemini.GeminiProvider`).
  - [x] Authenticated WebSocket streaming with initial state snapshot hydration.
- [x] **Phase 8A: Intelligent Model Routing Core** (`commit: 88ac57d`)
  - [x] `ModelRegistry` catalog tracking capabilities, context windows, and priorities.
  - [x] `ProviderRegistry` for provider lifecycle and health monitoring.
  - [x] `ModelRouter` for multi-criteria task matching.
  - [x] `ModelGateway` for unified completions and automated fallback failover.
- [x] **Phase 8B: Persistent Usage & Quota Subsystem** (`commit: a603114`)
  - [x] `UserQuota` and `UsageRecord` database models.
  - [x] Transactional row locking (`SELECT ... FOR UPDATE`) preventing quota oversubscription under concurrent load.
  - [x] User context propagation (`JWT $\rightarrow$ ResearchPipeline $\rightarrow$ AgentContext $\rightarrow$ ModelGateway $\rightarrow$ UsageRecord`).
  - [x] Quota-aware fallback routing.
- [x] **Documentation Architecture Synchronization** (`commit: a00949e`)
  - [x] Comprehensive documentation suite across root, `/docs/`, `/design/`, and roadmap specs.

---

## 🟡 Immediate Next Milestone: Phase 9 — Intelligent Knowledge Automation

- [ ] **Task 9.1: Automated End-to-End Ingestion Worker**
  - [ ] Implement automatic asynchronous pipeline daemon: `Upload $\rightarrow$ Validate $\rightarrow$ Extract $\rightarrow$ Normalize $\rightarrow$ Chunk $\rightarrow$ Embed $\rightarrow$ Index $\rightarrow$ Ready`.
  - [ ] Add background task worker updating document status from `pending` $\rightarrow$ `processing` $\rightarrow$ `ready`.
- [ ] **Task 9.2: PlannerAgent Knowledge Base Integration**
  - [ ] Inject knowledge base index summary into `PlannerAgent` prompt.
  - [ ] Enable Planner to evaluate: *"Do I have existing relevant knowledge?"* before scheduling external web searches.
- [ ] **Task 9.3: Automated Retrieval in Agent DAG**
  - [ ] Automatically route relevant private knowledge chunks to specialized research agents.
  - [ ] Provide unified hybrid context combining user documents and live web search.
- [ ] **Task 9.4: End-to-End Verification & Testing**
  - [ ] Write pytest integration tests for automated document upload through RAG retrieval.
  - [ ] Verify zero-touch indexing with PDF, DOCX, and image uploads.

---

## 🔮 Future Roadmap Backlog (Phases 10 – 26)

### Generation 1: Intelligent Research Core
- [ ] **Phase 10: Evidence & Citation Intelligence**
  - [ ] Fine-grained claim extraction and source linking with page/paragraph coordinates.
  - [ ] Source reliability scoring, contradictory claim detection, and citation-aware report generation.
- [ ] **Phase 11: Advanced Research Planning**
  - [ ] Deep problem decomposition into subquestions with specialized agent roles.

### Generation 2: Multimodal Intelligence
- [ ] **Phase 12: Advanced Multimodal Research**
  - [ ] Unified context across 50+ page PDFs, research papers, images, charts, audio, and video.
- [ ] **Phase 13: Dataset & Data Analysis Intelligence**
  - [ ] Tabular data processing (CSV, Excel, JSON) using deterministic Python calculation tools.
- [ ] **Phase 14: Document & Paper Intelligence**
  - [ ] Deep academic paper structure parsing and methodology comparison across preprints.

### Generation 3: Autonomous Research
- [ ] **Phase 15: Deep Research Engine**
  - [ ] Autonomous recursive execution loops with Critic-driven follow-up investigations.
- [ ] **Phase 16: Research Memory**
  - [ ] Persistent cross-session project memory allowing resumption months later.
- [ ] **Phase 17: Long-Term Knowledge Graph**
  - [ ] Entity-relationship graphs connecting researchers, claims, technologies, datasets, and concepts.

### Generation 4: Collaboration Platform
- [ ] **Phase 18: Projects & Workspaces**
  - [ ] Multi-tenant workspace hierarchy (`User $\rightarrow$ Workspace $\rightarrow$ Projects $\rightarrow$ Knowledge & Research`).
- [ ] **Phase 19: Team Collaboration**
  - [ ] Workspace roles (Owner, Researcher, Analyst, Reviewer, Viewer), shared projects, and collaborative report editing.

### Generation 5: AI Platform Intelligence
- [ ] **Phase 20: Intelligent Model Ecosystem**
  - [ ] Multi-variable routing optimization (Task, Quality, Latency, Cost budget, Context size, Provider health, Quota).
- [ ] **Phase 21: Model Evaluation System**
  - [ ] Automated benchmarking measuring model output accuracy, citation precision, and cost.
- [ ] **Phase 22: Agent Evaluation**
  - [ ] Observability dashboard tracking agent reasoning quality, hallucination rate, and execution efficiency.

### Generation 6: Production Product
- [ ] **Phase 23: Enterprise Security**
  - [ ] SOC 2 & GDPR compliance, immutable audit logging, data retention policies, and secret management.
- [ ] **Phase 24: Production Infrastructure**
  - [ ] Distributed task queues (Celery/Redis), worker autoscaling, S3/MinIO storage, and DB replication.
- [ ] **Phase 25: Public API & Developer Platform**
  - [ ] Public developer REST API, API key provisioning, rate limiting, and Python/TypeScript SDKs.
- [ ] **Phase 26: Research Automation**
  - [ ] Recurring scheduled research sweeps, topic monitoring, and automated alerting on new discoveries.
