# Execution Tracking: TASKS.md

This document tracks completed milestones, active work, blockers, technical debt, and planned roadmap items for the **Agentic Multimodal Research Platform**.

---

## 1. Status Dashboard

| Category | Status | Summary |
|---|---|---|
| **Current Active Milestone** | Phase 8B | User Quotas, Usage Telemetry & Fallback Refinements |
| **Test Suite Health** | 🟢 100% Passing | Unit and integration test suites passing across all packages |
| **Git Working Tree** | Clean (`develop/v1.1`) | Phase 8A committed; Phase 8B pending review & acceptance |

---

## 2. Milestone Execution Tracking

### 🟢 DONE (Completed & Verified)

- [x] **Phase 1: Foundation**
  - [x] Monorepo layout (`apps/api`, `apps/web`, `packages/*`).
  - [x] FastAPI async core with Pydantic v2 settings & `structlog` JSON logging.
  - [x] SQLAlchemy 2.0 async engine and SQLite/PostgreSQL parity.
  - [x] React + TypeScript + Vite frontend foundation shell.
  - [x] Docker Compose local infrastructure (PostgreSQL, ChromaDB, Redis, Ollama).

- [x] **Phase 2: Research MVP & DAG Pipeline**
  - [x] `PlannerAgent` with structured LLM decomposition.
  - [x] Persistent DAG task scheduler and execution engine.
  - [x] `WebResearchAgent` and `DocumentAnalysisAgent`.
  - [x] `ReportAgent` synthesis with citation preservation.
  - [x] Real-time WebSocket streaming endpoint (`/api/v1/research/{job_id}/ws`).

- [x] **Phase 3: Multimodal Document Ingestion**
  - [x] Text & Markdown parser.
  - [x] PDF parser with table extraction (`pdfplumber`).
  - [x] Word document parser (`python-docx`).
  - [x] Image vision analysis via Vision LLMs.
  - [x] Semantic and fixed chunking pipeline.
  - [x] Multipart upload API (`POST /api/v1/documents`).

- [x] **Phase 4: Agentic System & Tools**
  - [x] Extensible `ToolRegistry`.
  - [x] Built-in tools: `WebSearchTool`, `WebFetchTool` (with SSRF protection), `DocumentReadTool`, `KnowledgeSearchTool`.
  - [x] `CriticAgent` evidence verification and confidence scoring.
  - [x] Execution tracing persistence (`agent_runs`, `model_calls`).

- [x] **Phase 5: RAG & Retrieval Subsystem**
  - [x] Provider-agnostic `Embedder` protocol.
  - [x] ChromaDB adapter and `InMemoryVectorStore`.
  - [x] BM25 sparse lexical search.
  - [x] `HybridRetriever` with Reciprocal Rank Fusion (RRF, $k=60$).
  - [x] Cross-job `KnowledgeIndexer`.

- [x] **Phase 6: Production Hardening & Security**
  - [x] JWT access and refresh token authentication.
  - [x] Role-Based Access Control (`Admin`, `Researcher`, `Viewer`).
  - [x] Prometheus metrics exposition on `/metrics`.
  - [x] Kubernetes manifests (`infrastructure/k8s/`).

- [x] **Phase 7: Alignment & Persistence**
  - [x] Phase 7.1: Frontend dashboard job array mapping fix.
  - [x] Phase 7.2: Persistent PostgreSQL `users` table with Alembic migration (`001_create_users_table.py`).
  - [x] Phase 7.3: Official Google Gemini API provider (`GeminiProvider`); removal of unofficial `GeminiWeb2API`.

- [x] **Phase 8A: Intelligent Model Routing Core**
  - [x] `ModelRegistry` cataloging capabilities, task suitability, and priorities.
  - [x] `ProviderRegistry` managing active LLM, Vision, Embedding, and Reranker providers.
  - [x] `ModelRouter` capability and task-based selection.
  - [x] `ModelGateway` providing unified entry point, fallback retries, and latency telemetry.

---

### 🟡 IN PROGRESS

- [ ] **Phase 8B: User Quotas, Usage Telemetry & Fallback Refinements**
  - [x] Core schema draft for `UsageRecord` and `UserQuota`.
  - [x] Token count and cost estimation logic in `ModelGateway`.
  - [ ] Finalize Alembic migration for quota tables.
  - [ ] Wire quota enforcement interceptors into API route dependencies.
  - [ ] Finalize unit & integration tests for quota limit exhaustion.
  - [ ] User review, acceptance, and commit.

---

### 🔴 BLOCKED

- *No critical blockers currently.*

---

### 🔵 PLANNED (Future Milestones)

- [ ] **Phase 9: Audio & Video Ingestion**
  - [ ] Audio transcription pipeline using Whisper speech-to-text.
  - [ ] Video frame extraction and temporal visual analysis.
- [ ] **Phase 10: Multi-User Collaboration & Workspaces**
  - [ ] Workspace-level isolation and team sharing.
  - [ ] Collaborative research job comments and annotations.
- [ ] **Phase 11: Sandboxed Code Execution Tool**
  - [ ] Isolated Docker / gVisor code execution environment for data analytics tasks.

---

## 3. Known Technical Debt & Quality Backlog

1. **Frontend Authentication UI**: The backend has complete JWT/RBAC endpoints; the React frontend currently relies on development auto-auth or pre-seeded tokens. A dedicated Login/Register screen should be added.
2. **Postgres Vector Extension (pgvector)**: Currently vector search uses external ChromaDB; adding optional `pgvector` support directly in PostgreSQL would simplify single-database deployments.
3. **Staging Load Testing**: Run Locust load test scripts against Kubernetes cluster deployment to benchmark concurrent DAG execution limits.
