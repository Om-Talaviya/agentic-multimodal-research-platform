# Changelog: CHANGELOG.md

All notable changes to the **Agentic Multimodal Research Platform** are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased / Phase 8B] - In Review

### Added
- User quota tracking and daily token usage monitoring models (`UsageRecord`, `UserQuota`).
- Multi-tier provider fallback policies and cost estimation heuristics.
- Extended gateway telemetry hooks for token cost tracking.

---

## [1.1.0] - Phase 8A: Intelligent Model Routing Core

### Added
- Centralized `ModelGateway` providing unified entry for text completion, streaming, and vision analysis with automatic fallback retries (`packages/ai/gateway/model_gateway.py`).
- `ModelRegistry` cataloging model definitions, task suitability, priorities, and capabilities (`packages/ai/registry/model_registry.py`).
- `ProviderRegistry` managing active provider instances and consolidated health probes (`packages/ai/registry/provider_registry.py`).
- Task-based intelligent routing logic in `ModelRouter` (`packages/ai/providers/router.py`).

---

## [1.0.3] - Phase 7.3: Official Gemini Provider & Web2API Removal

### Changed
- Migrated Google Gemini integration from unofficial browser-scraping `GeminiWeb2API` to official `GeminiProvider` using official Google Gemini API keys and REST endpoints.
- Completely removed `gemini_web2api.py` and associated legacy integration tests.

---

## [1.0.2] - Phase 7.2: Persistent User Authentication

### Added
- PostgreSQL `users` database table with Alembic migration (`001_create_users_table.py`).
- Secure PBKDF2-HMAC-SHA256 password hashing and validation with per-user salt.
- `UserRepository` providing persistent lookup by username, email, and UUID.
- Integration test suite for user repository and database authentication lifecycles.

---

## [1.0.1] - Phase 7.1: Real-time Streaming & Dashboard Fixes

### Added
- Real-time WebSocket streaming endpoint (`/api/v1/research/{job_id}/ws`) with initial snapshot hydration and domain event broadcasting.
- Resilient WebSocket connection manager with exponential backoff auto-reconnection in frontend `ResearchDetail.tsx`.
### Fixed
- Corrected research job mapping in web dashboard (`Dashboard.tsx`) to support both array and paginated response objects.

---

## [1.0.0] - Phase 6: Production Readiness, Security & Monitoring

### Added
- JWT authentication framework with 24-hour access tokens and 7-day refresh tokens.
- Role-Based Access Control (RBAC) with `Admin`, `Researcher`, and `Viewer` roles.
- Prometheus metrics exposition endpoint (`/metrics`) tracking requests, latencies, and active jobs.
- Kubernetes deployment manifests (`infrastructure/k8s/`) and Prometheus/Grafana monitoring configurations.
- Server-Side Request Forgery (SSRF) protection rejecting private, loopback, link-local, and multicast IP ranges in web tools.

---

## [0.5.0] - Phase 5: RAG & Knowledge Retrieval Layer

### Added
- Provider-agnostic text `Embedder` protocol.
- `ChromaStore` vector database adapter and `InMemoryVectorStore` test double.
- BM25 sparse lexical search engine (`BM25Okapi`).
- `HybridRetriever` implementing Reciprocal Rank Fusion (RRF, $k=60$) combining dense and sparse search.
- Cross-job `KnowledgeIndexer` for historical evidence reuse.

---

## [0.4.0] - Phase 4: Agentic System & Observability

### Added
- Extensible `ToolRegistry` and built-in tools (`WebSearchTool`, `WebFetchTool`, `DocumentReadTool`, `KnowledgeSearchTool`).
- `CriticAgent` for evidence verification, contradiction detection, and confidence scoring (0.0 to 1.0).
- Execution trace persistence in `agent_runs` and `model_calls` tables.

---

## [0.3.0] - Phase 3: Multimodal Document Ingestion

### Added
- Document parsers for Plain Text/Markdown, PDF (`pdfplumber` with table extraction), Word documents (`python-docx`), and Images (Vision LLMs).
- Semantic and fixed-size chunking pipelines.
- Multipart document upload API (`POST /api/v1/documents`).

---

## [0.2.0] - Phase 2: Research MVP & DAG Execution

### Added
- `PlannerAgent` for structured LLM decomposition of research inquiries.
- Persistent Directed Acyclic Graph (DAG) task execution engine with dependency resolution.
- `WebResearchAgent` and `DocumentAnalysisAgent` worker implementations.
- `ReportAgent` for structured report synthesis with citation preservation.
- REST endpoints for jobs, tasks, sources, evidence, and reports.

---

## [0.1.0] - Phase 1: Foundation

### Added
- Monorepo structure with FastAPI backend, shared packages, and React (TypeScript + Vite) frontend.
- Async database connection with SQLAlchemy and Alembic.
- Pydantic Settings configuration management and `structlog` structured logging.
- Docker Compose local environment for PostgreSQL, ChromaDB, Redis, and Ollama.
