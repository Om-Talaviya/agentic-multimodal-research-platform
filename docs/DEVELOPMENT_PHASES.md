# Development Phases

## Phase 1: Foundation
**Status**: 🟢 COMPLETE

**Goal**: Working backend + frontend shell with basic API, config, logging, database, tests

### Deliverables

- [x] Repository structure
- [x] Architecture documentation
- [x] Backend (FastAPI) with:
  - [x] Configuration management (Pydantic Settings)
  - [x] Structured logging (structlog)
  - [x] Database connection (SQLAlchemy async)
  - [x] Basic health check endpoint
  - [x] Research job CRUD API
  - [x] Error handling middleware
- [x] Frontend foundation (React + TypeScript + Vite) with:
  - [x] Project setup
  - [x] Basic layout/components
  - [x] API client
  - [x] Research job creation form shell
  - [x] Job status display shell
- [x] Shared packages:
  - [x] `packages/shared` - config, logging, types, exceptions
  - [x] `packages/ai` - provider abstractions and gateway
  - [x] `packages/database` - models, repositories
- [x] Testing infrastructure:
  - [x] pytest configuration
  - [x] Unit test examples & suites
  - [x] Integration test setup
- [x] Docker Compose for local development
- [x] Git initialization with .gitignore
- [x] README with run instructions

### Commands to Verify

```bash
# Backend
cd apps/api && pytest tests/ -v
uvicorn src.main:app --reload
curl http://localhost:8000/api/v1/health

# Frontend
cd apps/web && npm run test
npm run dev
# Open http://localhost:5173
```

---

## Phase 2: Research MVP
**Status**: 🟢 COMPLETE

**Goal**: End-to-end research pipeline with planner + basic agents + persistent DAG execution + real-time WebSocket streaming

### Deliverables

- [x] Planner Agent implementation (structured LLM decomposition)
- [x] Web Research Agent (search + fetch)
- [x] Document Analysis Agent (text extraction)
- [x] Research Orchestrator (task execution, retries, lifecycle hooks)
- [x] Evidence storage & retrieval (SQLAlchemy models and repositories)
- [x] Basic Synthesis Agent
- [x] Report Generation Agent (structured synthesis with citation preservation)
- [x] Research pipeline integration with persistent/dynamic DAG execution
- [x] API endpoints for plan, tasks, sources, evidence, report
- [x] WebSocket for real-time updates (`/api/v1/research/{job_id}/ws` with snapshot + live DAG streaming)
- [x] Integration tests for full pipeline and WebSocket streaming

### Components

```
packages/agents/
  ├── planner/planner_agent.py
  ├── research/web_agent.py
  ├── research/document_agent.py
  ├── research/report_agent.py
  ├── synthesis/synthesis_agent.py
  └── orchestrator.py

packages/research/
  ├── events.py
  ├── pipeline.py
  ├── planner.py
  ├── verification.py
  ├── synthesis.py
  └── report.py
```

### Verification

```bash
# Create research job via API
curl -X POST http://localhost:8000/api/v1/research \
  -H "Content-Type: application/json" \
  -d '{"question": "What is quantum computing?"}'

# Poll job status, tasks, sources, evidence, and report
curl http://localhost:8000/api/v1/research/<job-id>
curl http://localhost:8000/api/v1/research/<job-id>/report
```

---

## Phase 3: Multimodal
**Status**: 🟢 COMPLETE

**Goal**: PDF, image, and document ingestion with vision models

### Deliverables

- [x] PDF parser (pdfplumber)
- [x] DOCX parser (python-docx)
- [x] Image parser (vision model via Gateway / Ollama / Gemini)
- [x] Table extraction
- [x] Ingestion pipeline orchestration
- [x] Chunking strategies (fixed, semantic)
- [x] Document upload API (`/api/v1/documents`)
- [x] Multimodal tests

### Components

```
packages/ingestion/
  ├── parsers/
  │   ├── base.py
  │   ├── text.py
  │   ├── pdf.py
  │   ├── docx.py
  │   └── image.py
  ├── chunking.py
  ├── normalization.py
  └── pipeline.py
```

### Verification

```bash
# Upload PDF
curl -X POST http://localhost:8000/api/v1/documents \
  -F "file=@research_paper.pdf" \
  -F "research_job_id=<job-id>"

# Verify ingestion
curl http://localhost:8000/api/v1/documents/<doc-id>
```

---

## Phase 4: Agentic System
**Status**: 🟢 COMPLETE

**Goal**: Specialized agents, tool system, critic/verifier, failure handling

### Deliverables

- [x] Tool framework with registry
- [x] Built-in tools (web_search, web_fetch with SSRF protection, document_read, knowledge_search)
- [x] Critic/Quality Agent (evidence auditing & verification scoring)
- [x] Agent memory (short/long term)
- [x] Retry and failure handling
- [x] Agent orchestration improvements
- [x] Parallel task execution via dynamic DAG
- [x] Agent trace logging (`agent_runs` & `model_calls` persistence)

### Components

```
packages/tools/
  ├── base.py
  ├── registry.py
  └── definitions/
      ├── web_search.py
      ├── web_fetch.py
      ├── document_read.py
      └── knowledge_search.py

packages/agents/
  ├── critic/critic_agent.py
  ├── memory.py
  └── tracing.py
```

### Verification

```bash
# Research with critic verification enabled
# Check agent traces in database
# Test failure recovery and retries
```

---

## Phase 5: RAG / Knowledge
**Status**: 🟢 COMPLETE

**Goal**: Embeddings, vector retrieval, evidence grounding

### Deliverables

- [x] Embedding provider abstraction (`Embedder`)
- [x] ChromaDB vector store adapter & InMemoryVectorStore
- [x] Hybrid retrieval (dense vector + sparse BM25 with Reciprocal Rank Fusion)
- [x] Reranker integration interface
- [x] Evidence grounding in synthesis
- [x] Citation generation & preservation
- [x] Knowledge persistence across jobs (`KnowledgeIndexer`)

### Components

```
packages/retrieval/
  ├── vector_store.py
  ├── chroma_store.py
  ├── in_memory_store.py
  ├── embedder.py
  ├── retriever.py
  ├── reranker.py
  ├── indexer.py
  └── bm25.py
```

### Verification

```bash
# Query vector store & hybrid retriever
# Verify citations in reports
# Test retrieval accuracy
```

---

## Phase 6: Production & Security
**Status**: 🟢 COMPLETE (Core Roadmap Capabilities)

**Goal**: Production-ready deployment with auth, monitoring, security

### Deliverables

- [x] Authentication (JWT access & refresh token lifecycle)
- [x] Authorization (RBAC with Admin, Researcher, Viewer roles)
- [x] Rate limiting
- [x] Security hardening (SSRF rejection, prompt injection detection, upload validation)
- [x] Prometheus metrics (`/metrics` endpoint)
- [x] Grafana dashboard configuration
- [x] Alerting rules configuration
- [x] Kubernetes manifests (`infrastructure/k8s/`)
- [x] CI/CD pipeline
- [ ] Load testing on staging cluster
- [x] Documentation

### Components

```
packages/shared/
  ├── auth.py
  └── security.py
infrastructure/
  ├── k8s/
  └── monitoring/
```

### Verification

```bash
# Verify Prometheus metrics
curl http://localhost:8000/metrics

# Test JWT login and protected endpoint access
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "adminpassword"}'
```

---

## Phase 11: Advanced Research Planning
**Status**: 🟢 COMPLETE (Generation 1: Intelligent Research Core)

**Goal**: Hierarchical subquestion decomposition, strategic query trees, ambiguity scoring, dynamic agent capability routing, and closed-loop adaptive replanning.

### Deliverables:
- [x] Hierarchical `QueryTreeNode` multi-level tree generator breaking complex inquiries into domain-focused sub-investigations.
- [x] Quantitative `ambiguity_score` ($0.0 - 1.0$) and `InferredScope` resolution.
- [x] Dynamic agent role and capability matching.
- [x] Closed-loop adaptive replanning (`PlannerAgent.replan()`) when `CriticAgent` detects evidentiary gaps or critical contradictions.
- [x] Real-time event streaming (`plan_decomposed`, `task_spawned`, `dag_replanned`).
- [x] Interactive `QueryTreeViewer.tsx` React component in `apps/web`.
- [x] Unit test suites in `packages/agents/tests/test_planner_advanced_planning.py`.

---

## Current Status Summary

| Phase | Milestone | Status | Test Coverage |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Foundation | 🟢 COMPLETE | Full backend, DB, API & test infra |
| **Phase 2** | Research MVP | 🟢 COMPLETE | DAG, agents, synthesis, report, WebSocket streaming |
| **Phase 3** | Multimodal Ingestion | 🟢 COMPLETE | Text, PDF, DOCX, Vision Image parsing & chunking |
| **Phase 4** | Agentic System | 🟢 COMPLETE | Tools, SSRF defense, Critic, tracing, retries |
| **Phase 5** | RAG / Knowledge Layer | 🟢 COMPLETE | Hybrid RRF, Embedder, BM25, Chroma adapter |
| **Phase 6** | Production & Security | 🟢 COMPLETE | JWT, RBAC, Prometheus metrics, K8s manifests |
| **Phase 7** | Application Maturity | 🟢 COMPLETE | Persistent DB users, official Gemini SDK, auth WebSockets |
| **Phase 8A**| Intelligent Model Routing | 🟢 COMPLETE | ModelRegistry, ProviderRegistry, ModelRouter, ModelGateway |
| **Phase 8B**| Usage & Quotas Subsystem | 🟢 COMPLETE | UserQuota, row-locking concurrency, quota-aware fallback |
| **Phase 9** | Intelligent Knowledge Auto| 🟢 COMPLETE | Dual-indexing (Dense+BM25), document lifecycle, Planner KB |
| **Phase 10**| Evidence & Citation Intel | 🟢 COMPLETE | Coordinate anchoring, contradiction taxonomy, confidence score |
| **Phase 11**| Advanced Research Planning| 🟢 COMPLETE | Query trees, ambiguity score, dynamic capability & replanning |

### Immediate Focus Areas
1. **Phase 12: Advanced Multimodal Research** (Unified context across 50+ page PDFs, research papers, images, charts, audio, video).
2. **Phase 13: Dataset & Data Analysis Intelligence** (Tabular data processing with deterministic calculation tools).