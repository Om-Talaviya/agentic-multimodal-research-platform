# Changelog: CHANGELOG.md

All notable changes to the **Agentic Multimodal Research Platform** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2026-09-12 (Branch: `develop/v1.1`)

### Added
- **Phase 11: Advanced Research Planning**:
  - Implemented hierarchical Subquestion Decomposition and Query Trees (`QueryTreeNode`) for multi-level strategic planning.
  - Added quantitative ambiguity evaluation (`ambiguity_score`) and autonomous parameterization of research boundaries (`InferredScope`).
  - Added dynamic agent role and capability matching, mapping sub-inquiries to specialized agent personas with execution contracts.
  - Implemented closed-loop Adaptive Replanning (`PlannerAgent.replan()`) triggered dynamically when `CriticAgent` detects evidentiary gaps or critical contradictions during execution.
  - Extended `ResearchTask` and `DBResearchTask` with `parent_task_id`, `is_dynamic`, and `depth` metadata.
  - Added `plan_decomposed`, `task_spawned`, and `dag_replanned` WebSocket events to `ResearchEventType`.
  - Created interactive `QueryTreeViewer.tsx` React component in `apps/web` with branch expand/collapse, ambiguity indicators, and live execution status.
  - Added unit test suite in `packages/agents/tests/test_planner_advanced_planning.py`.
- **Phase 10: Evidence & Citation Intelligence**:
  - Implemented fine-grained claim extraction and coordinate anchoring (`CitationCoordinates`) mapping claims to exact document coordinates (`page_number`, `paragraph_index`, `table_row`, `table_col`, `char_start`, `char_end`, `exact_quote`).
  - Added structured `Citation` and `Contradiction` models with SQLite and PostgreSQL 16 JSONB cross-compatibility.
  - Implemented pairwise Contradiction Detection Engine in `CriticAgent` with classification taxonomy (`direct_conflict`, `numerical_discrepancy`, `methodological_divergence`).
  - Upgraded `ReportAgent` to synthesize nested citations per finding, preserve the contradictions matrix, and calculate an overall quantitative factual confidence score (`confidence_score`).
  - Integrated full end-to-end evidence citation flow across `ResearchPipeline`, database models, and API serialization.
  - Added TypeScript interfaces in `apps/web/src/types/research.ts` (`Citation`, `CitationCoordinates`, `Contradiction`).
  - Added comprehensive test suites: `test_citation_intelligence.py`, `test_critic_contradiction_detection.py`, and `test_report_citation_synthesis.py`.
- **Phase 9: Intelligent Knowledge Automation**:
  - Automated zero-touch ingestion and dual-indexing (`Upload $\rightarrow$ Validate $\rightarrow$ Extract $\rightarrow$ Chunk $\rightarrow$ Embed $\rightarrow$ Index $\rightarrow$ Ready`).
  - Added document processing status lifecycle (`pending` $\rightarrow$ `processing` $\rightarrow$ `ready` / `failed`) in `Document` model and repository.
  - Integrated `KnowledgeIndexer` into `IngestionPipeline` for immediate `VectorStore` (embeddings) and `BM25Index` (lexical tokens) population.
  - Enhanced `PlannerAgent` with knowledge-base awareness, enabling the planner to inspect available domain documents before decomposing inquiries into the Task DAG.
  - Enhanced `DocumentAnalysisAgent` to support hybrid semantic retrieval (`KnowledgeSearchTool`) alongside direct document reading.
  - Added REST endpoints for knowledge base operations: `GET /api/v1/documents/search`, `POST /api/v1/documents/{id}/reindex`, and cascading `DELETE /api/v1/documents/{id}`.
- **Phase 8B: Persistent Usage & Quota Subsystem** (`commit: a603114`):
  - Added `UserQuota` model supporting configurable token and cost limits (`NULL` = unlimited).
  - Added `UsageRecord` model capturing per-inference telemetry (`input_tokens`, `output_tokens`, `total_tokens`, `estimated_cost`, `latency_ms`).
  - Added `UsageRepository` with transactional row-level locking (`SELECT ... FOR UPDATE`) to prevent race conditions during concurrent agent calls.
  - Verified concurrency guarantees with test suite (10 concurrent workers @ 20 tokens against 50-token quota resulting in 0 oversubscription).
  - Added quota-aware model fallback routing.
  - Propagated authenticated `user_id` from JWT auth down into `ResearchPipeline`, `AgentOrchestrator`, and `AgentContext`.
- **Comprehensive Documentation Architecture** (`commit: a00949e`):
  - Established synchronized documentation across `/README.md`, `/AGENTS.md`, `/docs/` (PRD, TRD, ARCHITECTURE, backend-schema, flow, decisions, CHANGELOG), `/design/ui-ux.md`, and `/TODO.md`.
  - Formalized 6-generation product roadmap spanning Phases 9 to 26.
- **Phase 8A: Intelligent Model Routing & Multi-Provider Gateway** (`commit: 88ac57d`):
  - Created `ModelRegistry` dynamic capability catalog (`STREAMING_RESPONSE`, `VISION_ANALYSIS`, `FACTUAL_EXTRACTION`, `SYNTHESIS`).
  - Created `ProviderRegistry` for active provider lifecycle and health monitoring.
  - Created `ModelRouter` for multi-criteria task matching and priority scoring.
  - Created `ModelGateway` for unified completion, streaming, vision invocation, and automated rate limit/error fallback failover.

---

## [1.0.0] - 2026-09-08

### Added
- **Phase 7: Application Maturity & Authentication Completion**:
  - Phase 7.1: Fixed research job response mapping in web dashboard.
  - Phase 7.2: Added persistent PostgreSQL `users` table, Alembic migration (`001_create_users_table.py`), and PBKDF2 password hashing.
  - Phase 7.3: Migrated to official Google Gemini SDK (`ai.providers.gemini.GeminiProvider`); deleted legacy unofficial `GeminiWeb2API`.
  - Added authenticated real-time WebSocket streaming (`/api/v1/research/{id}/ws`) with initial state snapshot hydration.
- **Phase 6: Production & Security**:
  - Added JWT access/refresh token lifecycle and RBAC (`Admin`, `Researcher`, `Viewer`).
  - Added SSRF protection in `WebFetchTool` with strict private IP and metadata endpoint filtering.
  - Added Prometheus metrics exposition (`/metrics`) and Kubernetes deployment manifests.
- **Phase 5: Hybrid RAG & Knowledge Layer**:
  - Implemented Reciprocal Rank Fusion (RRF) combining dense ChromaDB vector search and sparse BM25 lexical search.
  - Added document chunking with metadata preservation.
- **Phase 4: Agentic System Core**:
  - Built autonomous agent hierarchy: `PlannerAgent`, `WebResearchAgent`, `DocumentAnalysisAgent`, `CriticAgent`, and `ReportAgent`.
  - Added DAG execution engine with topological dependency resolution.
- **Phase 3: Multimodal Ingestion Pipeline**:
  - Added native PDF extraction with table detection (`pdfplumber`).
  - Added DOCX extraction (`python-docx`).
  - Added Image extraction via Vision LLMs (`Pillow`).
- **Phase 2: Research MVP**:
  - Implemented initial end-to-end research workflow from inquiry formulation to report generation.
- **Phase 1: Foundation**:
  - Established modular monorepo structure with FastAPI backend, SQLAlchemy 2.0 Async, and React 18 / Vite frontend.
