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

- [x] **Phase 14: Document & Paper Intelligence**
  - [x] Academic paper structure parsing: Implemented `AcademicPaperParser` in `packages/ingestion/src/ingestion/parsers/academic.py` extracting hierarchical section trees (`PaperSection`), metadata (title, authors, affiliations, abstract), and limitations summaries.
  - [x] Bibliographic extraction & citation matching: Structured `BibEntry` models, parsing inline reference markers (`[1]`, `[1, 2]`, `(Smith et al., 2024)`) and matching to References section entries with DOIs/arXiv IDs.
  - [x] Section-aware semantic chunking: Enhanced `SemanticChunker` to preserve academic section boundaries, tagging chunks with `section_title`, `section_type`, `paper_title`, and `authors` for targeted hybrid RAG.
  - [x] Academic research tooling: Created `PaperAnalysisTool` (dimension extraction, section queries, benchmark parsing) and `MethodologyComparisonTool` (cross-paper methodology comparison matrices).
  - [x] Agent integration: Equipped `DocumentAnalysisAgent` with academic paper parsing and comparative analysis tools.
  - [x] Interactive UI: Built `PaperViewer.tsx` (section tree sidebar, abstract, inline citations) and `ComparisonMatrix.tsx` (side-by-side methodology diffs).
  - [x] Unit test suites: Added `test_academic_parser.py` and `test_paper_analysis.py`.

---

- [x] **Phase 15: Deep Research Engine**
  - [x] Multi-round autonomous research orchestration: Built `DeepResearchEngine` in `packages/research/src/research/deep_research.py` orchestrating recursive hypothesis generation, dynamic DAG subtask rescheduling, and Critic re-verification loops.
  - [x] Recursive gap & hypothesis synthesis: Upgraded `CriticAgent` to audit evidence coverage, isolate unresolved gaps (`gap_queries`), and formulate suggested follow-up hypotheses.
  - [x] Adaptive DAG expansion: Enhanced `PlannerAgent.replan()` to accept deep iteration indices and transform gap queries and hypotheses into prioritized investigation subtasks.
  - [x] Strict convergence guardrails: Enforced threshold $\tau \ge 0.85$, maximum iteration ceiling (`max_iterations`), and diminishing returns cutoff ($\Delta \tau < 0.02$).
  - [x] Real-time iteration telemetry: Defined deep research event types and WebSocket broadcast for live iteration status and hypothesis tracking.
  - [x] Interactive Deep Research UI: Built `DeepResearchTracker.tsx` with multi-round iteration stepper, confidence gauge, hypothesis status badges, and gap resolution explorer.
  - [x] Automated test suites: Added `test_deep_research.py`, `test_deep_critic.py`, and verified 100% passing across all 247 tests.

---

- [x] **Phase 16: Research Memory**
  - [x] Persistent cross-session project memory architecture: Created `DBResearchMemory` database model with PostgreSQL 16 & SQLite cross-compatibility (`GUID`, `JSONType`), indexes, and access counters.
  - [x] Memory persistence repository: Built `MemoryRepository` with CRUD, tag filtering, access tracking, and text search across title/content.
  - [x] Autonomous memory manager: Implemented `ResearchMemoryManager` with automatic knowledge consolidation from research reports (`store_memories_from_report`), semantic recall (`recall_memories`), and prompt formatting.
  - [x] Pipeline & Agent memory integration: Connected `ResearchPipeline` to recall memories during planning (`run_planning`) and auto-persist memories upon report completion (`run_report_generation`). Upgraded `PlannerAgent` prompt guidelines.
  - [x] Agent memory tools: Built and registered `RecallMemoryTool` and `StoreMemoryTool` for agent-level memory operations.
  - [x] REST API endpoints: Created `/api/v1/memory` routes for listing, creating, searching/recalling, updating, and deleting memories.
  - [x] Interactive UI Studio: Built `ResearchMemoryViewer.tsx` and `MemoryPage.tsx` with memory type filters, semantic recall, tags, and memory creation modal. Added Memories tab to `ResearchDetail.tsx` and `/memory` navigation route.
  - [x] Comprehensive test suites: Added `test_memory_repository.py`, `test_research_memory.py`, `test_memory_tools.py`, `test_memory_api.py`, verified 256/256 tests passing.

---

- [x] **Phase 17: Long-Term Knowledge Graph**
  - [x] Graph database persistence: Created `DBKnowledgeEntity` and `DBKnowledgeRelation` models with dialect-safe `GUID` and `JSONType`, indexed foreign keys, and properties JSON.
  - [x] Graph persistence repository: Built `KnowledgeGraphRepository` with entity CRUD, canonicalization, relationship CRUD, k-hop BFS subgraph extraction, and shortest path traversal.
  - [x] Autonomous graph engine: Implemented `KnowledgeGraphEngine` with automated entity/relation extraction from findings/reports, Graph-Augmented RAG (`GraphRAG`) context builder, and multi-hop path search.
  - [x] Agent graph tools: Created and registered `QueryKnowledgeGraphTool`, `ExtractGraphTripletsTool`, and `FindRelationPathTool`.
  - [x] REST API endpoints: Built `/api/v1/graph` routes (`GET /nodes`, `POST /nodes`, `GET /nodes/{id}`, `DELETE /nodes/{id}`, `GET /edges`, `POST /edges`, `DELETE /edges/{id}`, `GET /subgraph`, `GET /paths`, `POST /extract`, `GET /stats`).
  - [x] Interactive UI Studio: Developed `KnowledgeGraphViewer.tsx` and `KnowledgeGraphPage.tsx` with interactive SVG canvas, entity-type color coding, node inspector, multi-hop pathfinder, and triplet extraction. Added Knowledge Graph tab to `ResearchDetail.tsx` and `/graph` navigation route.
  - [x] Comprehensive test suites: Added `test_knowledge_graph_repository.py`, `test_knowledge_graph_engine.py`, `test_knowledge_graph_tools.py`, `test_graph_api.py`, verified 265/265 tests passing.

---

- [x] **Phase 18: Projects & Workspaces**
  - [x] Multi-tenant workspace database persistence: Created `DBWorkspace`, `DBWorkspaceMember`, and `DBProject` models in `packages/database/src/database/models/workspace.py` with dialect-safe `GUID`, `JSONType`, multi-role membership (`owner`, `admin`, `researcher`, `member`, `viewer`), and unique slug generation.
  - [x] Scoped foreign keys: Added `workspace_id` and `project_id` foreign keys to `ResearchJob`, `Document`, `DBResearchMemory`, and `DBKnowledgeEntity`.
  - [x] Workspace & Project persistence repositories: Implemented `WorkspaceRepository` and `ProjectRepository` in `packages/database/src/database/repositories/` with auto-provisioning of personal default workspaces and projects, membership checks, and aggregate metric overview queries.
  - [x] REST API endpoints: Built `/api/v1/workspaces` and `/api/v1/projects` routes with CRUD, project creation, member management, and metric aggregation in `apps/api/src/api/routes/`.
  - [x] Pipeline & Document integration: Upgraded `ResearchPipeline`, `IngestionPipeline`, and API routes (`/research`, `/documents`) to accept, propagate, and filter by `workspace_id` and `project_id`.
  - [x] Interactive UI Studio: Built `WorkspaceContext.tsx` global provider, `WorkspaceSelector.tsx` dropdown in sidebar navigation, and dedicated `ProjectsPage.tsx` management dashboard in `apps/web`.
  - [x] Automated unit and integration test suites: Added `test_workspace_project_repo.py` and `test_workspaces_projects_api.py`, verified 100% passing across all 270 monorepo tests.

---

- [x] **Phase 19: Team Collaboration**
  - [x] Collaborative database models: Implemented `DBWorkspaceInvite`, `DBReportAnnotation`, and `DBWorkspaceActivity` models in `packages/database/src/database/models/collaboration.py` with crypto token generation, 7-day expiration, and dialect-safe `GUID`/`JSONType`.
  - [x] Collaboration repositories: Built `WorkspaceInviteRepository`, `ReportAnnotationRepository`, and `WorkspaceActivityRepository` in `packages/database/src/database/repositories/collaboration_repo.py` with token lookup/redemption, member role upgrades, report inline comments with quote anchoring, 1-click comment resolution, and activity feed logging.
  - [x] REST API endpoints: Created complete collaboration routes in `apps/api/src/api/routes/collaboration.py` (`/api/v1/workspaces/{id}/invites`, `/api/v1/invites/{token}`, `/api/v1/invites/{token}/accept`, `/api/v1/invites/{id}`, `/api/v1/reports/{id}/annotations`, `/api/v1/annotations/{id}/resolve`, `/api/v1/annotations/{id}`, `/api/v1/workspaces/{id}/activities`, `/api/v1/projects/{id}/activities`).
  - [x] Interactive UI Studio: Built `WorkspaceMembersModal.tsx` (member roster, email invitations, token copy, invite revocation) and `ReportAnnotationsDrawer.tsx` (report quote highlights, threaded comments, status filtering, resolution). Integrated into `ProjectsPage.tsx` and `ResearchDetail.tsx`.
  - [x] Automated test suites: Added `test_collaboration_repo.py` and `test_collaboration_api.py`, verified 100% passing across all 276 monorepo tests.

---

## 🟡 Immediate Next Milestone: Phase 20 — Intelligent Model Ecosystem

### Generation 5: AI Platform Intelligence
- [ ] **Phase 20: Intelligent Model Ecosystem**
  - [ ] Multi-variable routing optimization (Task, Quality, Latency, Cost budget, Context size, Provider health, Quota).
  - [ ] Dynamic Pareto-frontier model selector with configurable cost/speed preferences.
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
