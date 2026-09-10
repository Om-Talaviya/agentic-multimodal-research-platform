# System Architecture Specification: ARCHITECTURE.md

This document defines the authoritative, production system architecture of the **Agentic Multimodal Research Platform** (Architecture v1.1).

---

## 1. High-Level Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                   Presentation Layer: React SPA (apps/web)               │
│         Dashboard  •  New Research  •  Research Detail  •  Settings      │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │ HTTPS / WSS
┌────────────────────────────────────▼─────────────────────────────────────┐
│                      FastAPI API Gateway (apps/api)                      │
│                                                                          │
│  ┌─────────────────────────┐  ┌───────────────────────────────────────┐  │
│  │  Authentication & RBAC  │  │  WebSocket Connection Manager         │  │
│  │  (JWT, PBKDF2, Users)   │  │  (Snapshot hydration, live event bus) │  │
│  └─────────────────────────┘  └───────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  API Endpoints: /auth, /research, /documents, /models, /health     │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          ▼                          ▼                          ▼
┌───────────────────┐      ┌───────────────────┐      ┌────────────────────┐
│ Database Layer    │      │ Research Pipeline │      │ AI Engine          │
│ (packages/        │      │ & Orchestration   │      │ (packages/ai)      │
│  database)        │      │ (packages/        │      │                    │
│                   │      │  research)        │      │  ModelGateway      │
│ - Repositories    │      │                   │      │        │           │
│ - SQLAlchemy Async│◄────►│ - DAG Engine      │◄────►│  ModelRouter       │
│ - Alembic         │      │ - Event Bus       │      │   ├── ModelReg.    │
│ - PostgreSQL /    │      │ - PlannerAgent    │      │   └── ProviderReg. │
│   SQLite          │      │ - Synthesis       │      │        │           │
└───────────────────┘      └─────────┬─────────┘      │   Providers        │
                                     │                │   - Ollama         │
                                     ▼                │   - Gemini         │
                           ┌───────────────────┐      │   - OpenAI-compat  │
                           │ Agent Framework   │      └────────────────────┘
                           │ (packages/        │
                           │  agents)          │
                           │                   │
                           │ - WebAgent        │
                           │ - DocumentAgent   │
                           │ - CriticAgent     │
                           │ - ReportAgent     │
                           └─────────┬─────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    ▼                                 ▼
         ┌─────────────────────┐           ┌─────────────────────┐
         │ Tool Registry       │           │ Knowledge & RAG     │
         │ (packages/tools)    │           │ (packages/retrieval)│
         │                     │           │                     │
         │ - WebSearchTool     │           │ - Embedder          │
         │ - WebFetch (SSRF)   │           │ - HybridRetriever   │
         │ - DocumentReadTool  │           │   (ChromaDB + BM25) │
         │ - KnowledgeSearch   │           │ - Reciprocal Rank   │
         └─────────────────────┘           │   Fusion (RRF)      │
                                           └─────────────────────┘
```

---

## 2. Core Subsystems & Responsibilities

### 2.1 API & Presentation Layer (`apps/api` & `apps/web`)
- **FastAPI Core**: Handles request routing, dependency injection (`api.dependencies`), validation schemas, and Prometheus instrumentation.
- **WebSocket Streaming**: Bi-directional WebSocket manager delivering snapshot state on connect followed by real-time domain events via `ResearchEventBus`.
- **JWT & RBAC**: Enforces role-based permissions (`research:create`, `research:read`, `documents:upload`) with secure PBKDF2-HMAC-SHA256 password hashing.

### 2.2 Research Pipeline & DAG Task Execution (`packages/research`)
- **Pipeline Runner**: Coordinates end-to-end execution of a research inquiry.
- **Dynamic Task DAG**: Executes independent research tasks concurrently, resolving dependencies dynamically and propagating results downstream.
- **Event Bus (`ResearchEventBus`)**: Publishes granular events (`job_started`, `tasks_created`, `task_started`, `sources_added`, `evidence_added`, `verification_completed`, `report_generated`, `job_completed`).

### 2.3 Agent Framework (`packages/agents`)
- **`PlannerAgent`**: Uses structured LLM reasoning to decompose inquiries into a typed DAG.
- **`WebResearchAgent`**: Discovers external sources and queries search engines.
- **`DocumentAnalysisAgent`**: Ingests and inspects local multi-format documents.
- **`CriticAgent`**: Audits collected claims, calculates confidence metrics, and flags contradictions.
- **`ReportAgent`**: Synthesizes verified findings into a structured, citation-preserved document.

### 2.4 Multi-Provider AI Engine (`packages/ai`)
- **`ModelGateway`**: Single point of contact for application code; handles execution timeouts, automatic fallback retry routing, and telemetry capture.
- **`ModelRouter`**: Selects candidate models based on task suitability, required capabilities (`VISION`, `STREAMING`, `JSON_OUTPUT`), and locality preference.
- **`ModelRegistry`**: Dynamic catalog of model definitions, capability flags, priorities, and token limits.
- **`ProviderRegistry`**: Provider lifecycle manager supporting local `OllamaProvider`, official `GeminiProvider`, and `OpenAICompatibleProvider`.

### 2.5 Hybrid RAG & Knowledge Subsystem (`packages/retrieval`)
- **`Embedder`**: Provider-agnostic text embedding generator.
- **Dense Vector Store**: `ChromaDB` adapter with cosine distance similarity search.
- **Sparse Lexical Index**: In-memory `BM25Okapi` sparse keyword search.
- **`HybridRetriever`**: Merges vector and keyword search candidates via Reciprocal Rank Fusion (RRF, $k=60$).

### 2.6 Database & Persistence Layer (`packages/database`)
- **SQLAlchemy 2.0 Async**: Non-blocking database session management.
- **Repository Pattern**: Specialized repositories (`ResearchJobRepository`, `TaskRepository`, `SourceRepository`, `EvidenceRepository`, `DocumentRepository`, `ReportRepository`, `AgentRunRepository`, `UserRepository`).
- **Alembic**: Database schema versioning and automated migrations.

---

## 3. Major Package Boundaries

```
packages/
├── ai/          # ModelGateway, ModelRouter, ModelRegistry, ProviderRegistry, Providers
├── agents/      # Autonomous specialized agents, memory, and tracing
├── research/    # Pipeline coordinator, DAG scheduler, EventBus, synthesis engine
├── ingestion/   # Document parsers (PDF, DOCX, Image, Text), chunkers, extractors
├── retrieval/   # VectorStore, Chroma adapter, BM25, HybridRetriever, Embedder
├── database/    # Declarative models, repositories, connection pool, Alembic migrations
├── tools/       # Extensible tool registry, SSRF-safe WebFetch, WebSearch, DocReader
└── shared/      # Config (Pydantic Settings), structlog, JWT auth, security utilities
```

---

## 4. Key Data Flows

### A. Research Request & Execution Flow
1. Client issues `POST /api/v1/research`.
2. `ResearchJobRepository` creates `ResearchJob` (status: `pending`).
3. Background worker executes `ResearchPipeline.run()`.
4. `PlannerAgent` decomposes query into `ResearchTask` records.
5. Task DAG executes parallel tasks:
   - Worker agents invoke tools via `ToolRegistry`.
   - Tool calls invoke `ModelGateway` for model completions.
   - Raw claims and source URLs are persisted to `sources` and `evidence`.
6. `CriticAgent` audits evidence confidence ratings.
7. `ReportAgent` synthesizes verified evidence into `reports`.
8. Status is updated to `completed` and streamed to connected WebSockets.

### B. Document Ingestion Flow
1. Client uploads file via `POST /api/v1/documents`.
2. MIME-type routing triggers specific parser (`PDFParser`, `DocxParser`, `ImageParser`, `TextParser`).
3. Extracted text and tables are split into `DocumentChunk` records via semantic chunking.
4. Chunks are embedded via `Embedder` and indexed into `ChromaDB` and `BM25`.
5. Document record and chunk metadata are saved to the database.

---

## 5. Security & Isolation Architecture

- **SSRF Defense**: `WebFetchTool` validates IP destinations before socket creation, rejecting private networks, loopbacks, link-local, and cloud metadata endpoints.
- **Input Sanitization**: Prompt injection detection algorithms screen incoming query strings.
- **RBAC**: Every API route validates JWT claims against granular permissions.
- **Token Security**: PBKDF2-HMAC-SHA256 password hashing with 100,000 iterations and per-user cryptographic salt.
