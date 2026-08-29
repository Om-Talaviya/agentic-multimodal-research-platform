# Development Phases

## Phase 1: Foundation (Current)

**Goal**: Working backend + frontend with basic API, config, logging, database, tests

### Deliverables

- [x] Repository structure
- [x] Architecture documentation
- [ ] Backend (FastAPI) with:
  - [ ] Configuration management (Pydantic Settings)
  - [ ] Structured logging (structlog)
  - [ ] Database connection (SQLAlchemy async)
  - [ ] Basic health check endpoint
  - [ ] Research job CRUD API
  - [ ] Error handling middleware
- [ ] Frontend (React + TypeScript + Vite) with:
  - [ ] Project setup
  - [ ] Basic layout/components
  - [ ] API client
  - [ ] Research job creation form
  - [ ] Job status display
- [ ] Shared packages:
  - [ ] `packages/shared` - config, logging, types, exceptions
  - [ ] `packages/ai` - provider abstractions (interfaces only)
  - [ ] `packages/database` - models, repositories
- [ ] Testing infrastructure:
  - [ ] pytest configuration
  - [ ] Unit test examples
  - [ ] Integration test setup with testcontainers
- [ ] Docker Compose for local development
- [ ] Git initialization with .gitignore
- [ ] README with run instructions

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

**Goal**: End-to-end research pipeline with planner + basic agents

### Deliverables

- [ ] Planner Agent implementation
- [ ] Web Research Agent (search + fetch)
- [ ] Document Analysis Agent (text extraction)
- [ ] Research Orchestrator (task execution)
- [ ] Evidence storage & retrieval
- [ ] Basic Synthesis Agent
- [ ] Report Generation Agent
- [ ] Research pipeline integration
- [ ] API endpoints for plan, tasks, sources, evidence, report
- [ ] WebSocket for real-time updates
- [ ] Integration tests for full pipeline

### New Components

```
packages/agents/
  ├── planner/planner_agent.py
  ├── research/web_agent.py
  ├── research/document_agent.py
  ├── synthesis/synthesis_agent.py
  ├── report/report_agent.py
  └── orchestrator.py

packages/research/
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

# Monitor via WebSocket or polling
# View final report
```

---

## Phase 3: Multimodal

**Goal**: PDF, image, and document ingestion with vision models

### Deliverables

- [ ] PDF parser (pdfplumber)
- [ ] DOCX parser (python-docx)
- [ ] Image parser (vision model via Ollama)
- [ ] Table extraction
- [ ] Ingestion pipeline orchestration
- [ ] Chunking strategies (fixed, semantic)
- [ ] Document upload API
- [ ] Multimodal tests

### New Components

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

**Goal**: Specialized agents, tool system, critic/verifier, failure handling

### Deliverables

- [ ] Tool framework with registry
- [ ] Built-in tools (web_search, web_fetch, document_read)
- [ ] Critic/Quality Agent
- [ ] Agent memory (short/long term)
- [ ] Retry and failure handling
- [ ] Agent orchestration improvements
- [ ] Parallel task execution
- [ ] Agent trace logging

### New Components

```
packages/tools/
  ├── base.py
  ├── registry.py
  └── definitions/
      ├── web_search.py
      ├── web_fetch.py
      └── document_read.py

packages/agents/
  ├── critic/critic_agent.py
  ├── memory.py
  └── tracing.py
```

### Verification

```bash
# Research with critic enabled
# Check agent traces in UI
# Test failure recovery
```

---

## Phase 5: RAG / Knowledge

**Goal**: Embeddings, vector retrieval, evidence grounding

### Deliverables

- [ ] Embedding provider abstraction
- [ ] ChromaDB vector store
- [ ] Hybrid retrieval (vector + keyword)
- [ ] Reranker integration
- [ ] Evidence grounding in synthesis
- [ ] Citation generation
- [ ] Knowledge persistence across jobs

### New Components

```
packages/retrieval/
  ├── vector_store.py
  ├── chroma_store.py
  ├── embedder.py
  ├── retriever.py
  └── reranker.py
```

### Verification

```bash
# Query vector store
# Verify citations in reports
# Test retrieval accuracy
```

---

## Phase 6: Production

**Goal**: Production-ready deployment with auth, monitoring, security

### Deliverables

- [ ] Authentication (JWT)
- [ ] Authorization (RBAC)
- [ ] Rate limiting
- [ ] Security hardening
- [ ] Prometheus metrics
- [ ] Grafana dashboards
- [ ] Alerting rules
- [ ] Kubernetes manifests
- [ ] CI/CD pipeline
- [ ] Load testing
- [ ] Documentation

### New Components

```
packages/shared/auth.py
infrastructure/k8s/
.github/workflows/
```

### Verification

```bash
# Deploy to staging
# Run load tests
# Verify monitoring
# Security scan
```

---

## Phase 7+: Future Expansion

- Audio/video processing
- Multi-user collaboration
- Advanced agent memory
- Custom model fine-tuning
- Plugin system
- Mobile app

---

## Current Status: Phase 1 In Progress

Next immediate steps:
1. Implement backend foundation (FastAPI app)
2. Implement frontend foundation (React app)
3. Create shared packages
4. Set up testing
5. Verify everything runs