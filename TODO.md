# Project Tasks & Roadmap: TODO.md

This document tracks all completed engineering milestones, the immediate active sprint, and the long-term backlog for the **Agentic Multimodal Research Platform (AI Research OS)**.

---

## 🟢 Completed Milestones (Phases 1 – 9)

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
- [x] **Phase 9: Intelligent Knowledge Automation**
  - [x] Automated end-to-end ingestion and dual-indexing (`Upload $\rightarrow$ Validate $\rightarrow$ Extract $\rightarrow$ Chunk $\rightarrow$ Embed $\rightarrow$ Index $\rightarrow$ Ready`).
  - [x] Document status lifecycle (`pending` $\rightarrow$ `processing` $\rightarrow$ `ready` / `failed`) with repo status update methods.
  - [x] `PlannerAgent` knowledge base integration inspecting local documents before decomposing inquiries.
  - [x] `DocumentAnalysisAgent` hybrid search integration with `KnowledgeSearchTool`.
  - [x] Document management REST endpoints (`GET /search`, `POST /{id}/reindex`, `DELETE /{id}`).
- [x] **Documentation Architecture Synchronization** (`commit: a00949e`)
  - [x] Comprehensive documentation suite across root, `/docs/`, `/design/`, and roadmap specs.

---

- [x] **Phase 10: Evidence & Citation Intelligence**
  - [x] Fine-grained claim extraction and coordinate anchoring (`page_number`, `paragraph_index`, `table_row`, `table_col`, `char_start`, `char_end`, `exact_quote`).
  - [x] Structured `Citation`, `CitationCoordinates`, and `Contradiction` models with SQLite / PostgreSQL 16 cross-compatibility.
  - [x] Contradiction Detection Engine in `CriticAgent` with pairwise taxonomy (`direct_conflict`, `numerical_discrepancy`, `methodological_divergence`).
  - [x] Citation-aware `ReportAgent` synthesis linking findings to structured citations and quantitative confidence index (`confidence_score`).
  - [x] Pipeline orchestration propagating contradictions and factual grounding scores through `ResearchPipeline`.
  - [x] TypeScript interfaces in `apps/web` (`Citation`, `CitationCoordinates`, `Contradiction`).
  - [x] Unit test suites (`test_citation_intelligence.py`, `test_critic_contradiction_detection.py`, `test_report_citation_synthesis.py`).

---

- [x] **Phase 11: Advanced Research Planning**
  - [x] **Task 11.1: Deep Subquestion Decomposition & Query Tree Generation**: Hierarchical `QueryTreeNode` multi-tier decomposition, ambiguity scoring ($0.0 - 1.0$), and inferred scope parameterization (`InferredScope`).
  - [x] **Task 11.2: Dynamic Agent Role & Capability Assignment**: Granular DAG routing matching subquestions to specialized agent personas with execution contracts.
  - [x] **Task 11.3: Adaptive Planning & Dynamic Replanning**: Closed-loop dynamic replanning (`PlannerAgent.replan()`) triggering `task_spawned` and `dag_replanned` when contradictions or evidentiary gaps are flagged.
  - [x] **Task 11.4: Interactive Research Planning Studio**: Real-time `QueryTreeViewer.tsx` component with expandable branch visualization and WebSocket progress streaming.
  - [x] **Task 11.5: Automated Verification**: Comprehensive unit test suite in `test_planner_advanced_planning.py`.

---

- [x] **Phase 12: Advanced Multimodal Research**
  - [x] Multimodal schema unification: Extended `CitationCoordinates` with `timestamp_start`, `timestamp_end`, `media_type`, `speaker`, `chart_data`.
  - [x] Speech & Audio Intelligence: Created `AudioParser` supporting `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg` with timestamped speech segments and speaker diarization.
  - [x] Video Understanding: Created `VideoParser` generating synchronized timeline events, dialogue transcripts, and keyframe snapshots.
  - [x] Scientific Chart & Diagram Parsing: Upgraded `ImageParser` to detect charts, extracting `ChartRef` models with structured JSON data series and Markdown data tables.
  - [x] Multimodal Chunking & Dual-Indexing: Upgraded `SemanticChunker` to preserve audio/video timestamps and chart series for vector and BM25 RRF indexing.
  - [x] API Whitelist Extension: Whitelisted audio/video MIME types and file extensions in `apps/api/src/api/routes/documents.py`.
  - [x] Interactive Multimodal UI: Built `MultimodalEvidenceViewer.tsx` studio component with audio/video badges, timestamp ranges, and interactive chart inspector.
  - [x] Automated Unit Test Suite: Added comprehensive test suite in `packages/ingestion/tests/test_multimodal_audio_video.py`.

---

- [x] **Phase 13: Dataset & Data Analysis Intelligence**
  - [x] Multimodal tabular ingestion: Created `TabularParser` for `.csv`, `.tsv`, `.xlsx`, `.xls`, `.json` with automated type inference, column statistics (mean, median, std dev, min/max, nulls, unique count), and markdown summary table generation.
  - [x] Deterministic mathematical calculation engine: Built `DataAnalysisTool` (descriptive statistics, aggregations, Pearson correlation, linear regression, filtering) and `DeterministicMathTool` (safe AST mathematical evaluator) enforcing **ADR 007** and **ADR 013** zero-hallucination standards.
  - [x] Agent integration: Equipped `DocumentAnalysisAgent` with `DataAnalysisTool` and `DeterministicMathTool` for deterministic data processing.
  - [x] API & Ingestion updates: Whitelisted dataset formats (`CSV`, `TSV`, `EXCEL`, `JSON`) in `DocumentFormat`, `SourceType`, and `/documents/upload` endpoint.
  - [x] Semantic chunking: Extended `SemanticChunker` with tabular profile chunking preserving column statistics and sample rows for dual vector/BM25 indexing.
  - [x] Interactive dataset UI: Developed `DatasetViewer.tsx` with summary overview, column profile metric tables, and raw data sample tabs.
  - [x] Unit test suites: Added `test_tabular_parser.py` and `test_data_analysis_tool.py`.

---

## 🟡 Immediate Next Milestone: Phase 14 — Document & Paper Intelligence

### Generation 2: Multimodal Intelligence
- [ ] **Phase 14: Document & Paper Intelligence**
  - [ ] Deep academic paper structure parsing (200+ page PDFs, section hierarchies, author metadata, abstract, bibliography).
  - [ ] Cross-paper methodology comparison, experimental result extraction, and research preprint synthesis.

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
