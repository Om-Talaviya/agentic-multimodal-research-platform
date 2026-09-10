# Technical Requirements Document (TRD)

## Project: Agentic Multimodal Research Platform
**Status**: Active / Production v1.1  
**Architecture Version**: 1.1 (Phase 8 Multi-Provider Architecture)  
**Last Updated**: September 2026  

---

## 1. System Architecture & Constraints

The Agentic Multimodal Research Platform is built upon a decoupled, asynchronous, layered architecture.

```
┌─────────────────────────────────────────────────────────────────┐
│                      Client Layer (React / Vite)                │
└────────────────────────────────┬────────────────────────────────┘
                                 │ HTTP / REST / WebSocket
┌────────────────────────────────▼────────────────────────────────┐
│                   FastAPI Application Gateway (apps/api)        │
│  - JWT Authentication Middleware                                │
│  - Role-Based Access Control (RBAC)                             │
│  - Research & Document Endpoints                                │
│  - Real-Time WebSocket Connection Manager                       │
└────────────────────────────────┬────────────────────────────────┘
                                 │
     ┌───────────────────────────┼──────────────────────────┐
     ▼                           ▼                          ▼
┌──────────────┐        ┌──────────────────┐       ┌─────────────────┐
│   Database   │        │     Research     │       │    AI Engine    │
│  Repository  │        │   Orchestrator   │       │   (ModelGateway)│
│    Layer     │        │  (packages/      │       │  (packages/ai)  │
│ (PostgreSQL/ │        │   research)      │       └────────┬────────┘
│   SQLite)    │        └────────┬─────────┘                │
└──────────────┘                 │                          │
                 ┌───────────────┴───────────────┐          │
                 ▼                               ▼          ▼
        ┌──────────────────┐           ┌──────────────────────┐
        │  Agent Framework │           │   Multi-Provider     │
        │ (Planner, Web,   │◄─────────►│   Model Routing      │
        │  Doc, Critic,    │           │ (Ollama, Gemini,     │
        │  Report Agents)  │           │  OpenAI-Compatible)  │
        └────────┬─────────┘           └──────────────────────┘
                 │
                 ▼
        ┌──────────────────┐
        │   Tools & RAG    │
        │ (SSRF-safe Fetch,│
        │  ChromaDB, BM25) │
        └──────────────────┘
```

### Architectural Constraints
- **Asynchronous Execution**: Zero synchronous blocking calls in the main event loop. All external network requests, database queries, and model inferences must use `async`/`await`.
- **Database Cross-Compatibility**: Fully compatible with PostgreSQL 16 (production) and SQLite (in-memory test suites) using SQLAlchemy JSON/UUID dialect wrappers.
- **Local-First Modularity**: Core pipeline must operate seamlessly without internet access when configured with local Ollama providers.

---

## 2. Technical Stack Specifications

### 2.1 Backend Core
- **Runtime**: Python 3.11+
- **Framework**: FastAPI (ASGI) with Uvicorn
- **Settings**: Pydantic v2 Settings (`BaseSettings`)
- **Logging**: `structlog` producing JSON-formatted context-bound log streams
- **Observability**: Prometheus client exposing metrics on `/metrics`

### 2.2 Database & Persistence
- **RDBMS**: PostgreSQL 16 (Production) / SQLite 3 (Testing)
- **Driver**: `asyncpg` for PostgreSQL, `aiosqlite` for SQLite
- **ORM**: SQLAlchemy 2.0 Async declarative models
- **Migrations**: Alembic with async `env.py` runner
- **Vector Store**: ChromaDB (via HTTP client adapter) and `InMemoryVectorStore` for testing
- **Caching & Pub/Sub**: Redis 7+

### 2.3 Frontend Application
- **Runtime**: Node.js 20+
- **Build Tool**: Vite 5+
- **UI Framework**: React 18 with TypeScript (strict mode enabled)
- **Styling**: Vanilla CSS custom property design system (`apps/web/src/index.css`)
- **Icons**: Lucide React
- **HTTP Client**: Axios with interceptors
- **WebSocket**: Native WebSocket API with exponential backoff auto-reconnect

---

## 3. AI & Model Routing Architecture (Phase 8A / 8B)

The AI layer is structured into four decoupled subsystems in `packages/ai`:

```
User / Agent Request
       │
       ▼
┌────────────────────────┐
│      ModelGateway      │  <- High-level complete(), stream_complete(), analyze_vision()
│                        │  <- Telemetry, retries, fallback routing orchestration
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│      ModelRouter       │  <- Capability matching, task suitability scoring
└─────┬────────────┬─────┘
      │            │
      ▼            ▼
┌───────────┐ ┌───────────────┐
│ModelReg.  │ │ProviderReg.   │
│(Metadata, │ │(Ollama, Gemini│
│ Task Map) │ │ OpenAI-compat)│
└───────────┘ └───────┬───────┘
                      │
                      ▼
               Concrete Provider (e.g. GeminiProvider, OllamaProvider)
```

### 3.1 Components
1. **`ModelRegistry`**: Maintains `ModelDefinition` instances specifying `capabilities` (`STREAMING`, `VISION`, `JSON_OUTPUT`), `task_suitability`, `priority`, and context window sizes.
2. **`ProviderRegistry`**: Manages active instances of `LLMProvider`, `VisionProvider`, `EmbeddingProvider`, and `RerankerProvider`.
3. **`ModelRouter`**: Computes best model-provider tuples based on explicit request, task type (`TaskType`), and capability constraints (`prefer_local`).
4. **`ModelGateway`**: Provides unified interface with automatic failover fallback across providers, response latency tracking, and execution metadata enrichment.

### 3.2 Task-Based Routing Types
- `STREAMING_RESPONSE`: Requires streaming token support.
- `VISION_ANALYSIS`: Requires multimodal image understanding capability.
- `FACTUAL_EXTRACTION`: Optimizes for high-precision extraction and JSON adherence.
- `PLANNING`: Optimizes for multi-step structured reasoning.
- `SYNTHESIS`: Optimizes for long-context comprehension and citation grounding.

---

## 4. Agentic Research Pipeline & DAG Execution

### 4.1 Planner & Task Graph
The `PlannerAgent` decomposes the research question into discrete tasks represented as a DAG.
Each `ResearchTask` contains:
- `id`: UUID
- `job_id`: UUID
- `type`: Task classification (e.g., `web_search`, `document_analysis`, `critic_verification`, `report_generation`)
- `agent`: Designated agent worker
- `depends_on`: List of predecessor task UUIDs
- `status`: `pending`, `running`, `completed`, `failed`

### 4.2 Research Orchestrator
- Performs topological sort of tasks.
- Spawns parallel worker coroutines for tasks whose dependencies are satisfied.
- Handles worker timeouts, exponential retries, and failure propagation.

### 4.3 Critic & Verification Subsystem
- The `CriticAgent` inspects extracted evidence against source material.
- Assigns a numeric `confidence` score (0.0 to 1.0) and verification status (`verified`, `refuted`, `unverified`).
- Generates `verification_notes` explaining flags or discrepancies.

---

## 5. Multimodal Ingestion Pipeline

The `packages/ingestion` subsystem handles document parsing and normalization:

| Format | Parser | Strategy |
|---|---|---|
| Plain Text / Markdown | `TextParser` | Direct UTF-8 decoding, frontmatter stripping |
| Adobe PDF | `PDFParser` (`pdfplumber`) | Text extraction, page indexing, embedded table extraction |
| Word Document | `DocxParser` (`python-docx`) | Paragraph styling, document hierarchy, table parsing |
| Images (PNG, JPG, WebP) | `ImageParser` (`Pillow` + Vision LLM) | Visual scene transcription, OCR text extraction via Gateway |

### Chunking Engine
- **Fixed / Sliding Window**: Configurable chunk size (default 1000 tokens) with overlap (default 100 tokens).
- **Semantic Chunking**: Splits on paragraph and header boundaries preserving document structural context.

---

## 6. RAG & Retrieval Subsystem

1. **Embedding**: `Embedder` protocol interfacing with `nomic-embed-text` (Ollama), `text-embedding-004` (Gemini), or OpenAI embeddings.
2. **Vector Search**: ChromaDB collection indexing with cosine distance metric.
3. **Lexical Search**: `BM25Okapi` sparse keyword search over document chunks.
4. **Hybrid Fusion**: Reciprocal Rank Fusion (RRF) algorithm:
   $$RRF\_Score(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$
   where $k=60$ and $r_m(d)$ is the rank of document $d$ in retrieval method $m$.

---

## 7. Security, Authentication & Non-Functional Requirements

### 7.1 Security Architecture
- **JWT Authentication**: HS256 algorithm with configurable secret key, 24-hour access expiration, and 7-day refresh token rotation.
- **Password Security**: PBKDF2-HMAC-SHA256 with 100,000 iterations and per-user cryptographic salt.
- **SSRF Hardening**: Network socket validation in `WebFetchTool` rejecting RFC 1918 private subnets, loopbacks, link-local, and cloud metadata addresses (`169.254.169.254`).
- **Prompt Injection Defense**: Input validation filters scanning for prompt hijacking signatures before agent dispatch.

### 7.2 Performance & Reliability
- **WebSocket Latency**: < 50ms event delivery overhead from backend event bus to connected web clients.
- **Database Concurrency**: Async connection pool (default pool size: 10, max overflow: 20).
- **Graceful Degradation**: If external cloud providers hit rate limits (HTTP 429), `ModelGateway` fails over to local Ollama fallback models.

### 7.3 Testing Standards
- Unit tests for all pure functions, parsers, and registries.
- Integration tests for database repositories, API endpoints, and WebSocket channels.
- Mocking of external model providers during CI test execution to guarantee zero network flakes.
