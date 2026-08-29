# Project Blueprint: Agentic Multimodal Research Platform

## 1. Project Overview

The Agentic Multimodal Research Platform is a production-grade system that enables users to submit research questions and have an agentic AI system autonomously conduct comprehensive research. The platform breaks down research requests, plans strategies, searches multiple sources, processes multimodal inputs, extracts evidence, verifies findings, and generates structured, well-cited research reports.

## 2. Requirements

### Functional Requirements
- **FR-1**: Accept natural language research questions/objectives
- **FR-2**: Decompose research into executable tasks via planner agent
- **FR-3**: Execute research tasks using specialized agents (web, document, multimodal, data)
- **FR-4**: Ingest and process multimodal inputs (text, PDF, DOCX, images, tables, URLs)
- **FR-5**: Extract, normalize, and store evidence with full provenance
- **FR-6**: Verify and cross-check evidence across sources
- **FR-7**: Synthesize findings using multiple AI agents with critique
- **FR-8**: Generate structured reports with citations and uncertainty quantification
- **FR-9**: Provide research status tracking and observability
- **FR-10**: Support configurable model providers (local and cloud)

### Non-Functional Requirements
- **NFR-1**: Modular architecture with provider abstractions
- **NFR-2**: Loose coupling between components
- **NFR-3**: Testable without expensive external API calls
- **NFR-4**: Observable execution traces for debugging
- **NFR-5**: Security by default (no secrets in code, input validation)
- **NFR-6**: Graceful degradation on partial failures
- **NFR-7**: Evidence-grounded outputs (traceable to sources)

## 3. Goals & Non-Goals

### Goals (MVP)
- Working research pipeline with planner + basic agents
- Multimodal ingestion (text, PDF, images)
- Local model support via Ollama
- Basic report generation with citations
- Observable execution traces

### Non-Goals (Phase 1)
- Full authentication/authorization
- Production deployment infrastructure
- Audio/video processing
- Advanced RAG with hybrid retrieval
- Multi-user collaboration
- Complex agent memory systems

## 4. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Layer (FastAPI)                      │
├─────────────────────────────────────────────────────────────────┤
│                     Research Orchestrator                       │
├──────────────┬──────────────┬──────────────┬───────────────────┤
│  Planner     │  Web Research│  Document    │  Multimodal       │
│  Agent       │  Agent       │  Analysis    │  Analysis Agent   │
│              │              │  Agent       │                   │
├──────────────┼──────────────┼──────────────┼───────────────────┤
│         Evidence Verification & Critic Agents                  │
├─────────────────────────────────────────────────────────────────┤
│              Synthesis & Report Generation Agents              │
├─────────────────────────────────────────────────────────────────┤
│                    Model Router / Provider Abstraction          │
├──────────┬──────────┬──────────┬──────────┬────────────────────┤
│  LLM     │  Vision  │Embedding │ Reranker │  Future Providers  │
│ Provider │ Provider │ Provider │ Provider │                    │
└──────────┴──────────┴──────────┴──────────┴────────────────────┘
          │          │          │          │
┌─────────┴──────────┴──────────┴──────────┴────────────────────┐
│                      Data Layer                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ PostgreSQL  │  │  ChromaDB   │  │  File Store │             │
│  │ (Relational)│  │  (Vectors)  │  │  (Assets)   │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

## 5. Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Backend | Python 3.11+ / FastAPI | Excellent AI/ML ecosystem, async support, type hints |
| Frontend | React 18 + TypeScript + Vite | Modern, fast HMR, strong typing |
| Relational DB | PostgreSQL + SQLAlchemy 2.0 | Mature, ACID, async support |
| Vector DB | ChromaDB | Local-first, simple API, good for embeddings |
| Message Queue | Redis + Celery | Reliable task queue, scheduling |
| Config | Pydantic Settings | Type-safe, env-based configuration |
| Logging | structlog + OpenTelemetry | Structured, observable |
| Testing | pytest / Vitest | Industry standard, good async support |
| LLM Provider | Ollama (local) + OpenAI-compatible | Local-first, extensible |
| Containerization | Docker + Docker Compose | Reproducible environments |

## 6. Repository Structure

```
project-root/
│
├── apps/
│   ├── api/                 # FastAPI backend
│   │   ├── src/
│   │   │   ├── main.py
│   │   │   ├── config.py
│   │   │   ├── database/
│   │   │   ├── models/
│   │   │   ├── schemas/
│   │   │   ├── api/
│   │   │   ├── services/
│   │   │   └── core/
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   └── Dockerfile
│   │
│   └── web/                 # React frontend
│       ├── src/
│       │   ├── components/
│       │   ├── pages/
│       │   ├── hooks/
│       │   ├── services/
│       │   ├── types/
│       │   └── utils/
│       ├── tests/
│       ├── package.json
│       └── Dockerfile
│
├── packages/                # Shared internal packages
│   ├── ai/                  # Model provider abstractions
│   ├── agents/              # Agent framework & implementations
│   ├── research/            # Research pipeline logic
│   ├── ingestion/           # Multimodal ingestion pipeline
│   ├── retrieval/           # Vector search & RAG
│   ├── database/            # Database abstractions
│   ├── tools/               # Tool definitions & registry
│   └── shared/              # Common utilities, types
│
├── tests/                   # Integration & e2e tests
│
├── docs/                    # Architecture documentation
│
├── scripts/                 # Utility scripts
│
├── infrastructure/          # Docker, k8s, terraform
│
├── .env.example
├── docker-compose.yml
├── README.md
└── pyproject.toml (root)
```

## 7. Database & Storage Architecture

### PostgreSQL (Relational)
- `users` - User accounts (future)
- `research_jobs` - Research requests and metadata
- `research_tasks` - Decomposed tasks with status
- `sources` - Collected sources with metadata
- `evidence` - Extracted evidence chunks with provenance
- `reports` - Generated reports
- `agent_runs` - Execution traces for observability
- `model_calls` - LLM call logs for debugging

### ChromaDB (Vector)
- Document chunks with embeddings
- Evidence embeddings for retrieval
- Source embeddings for deduplication

### File Storage
- Local filesystem (dev) / S3-compatible (prod)
- Organized by research_job_id
- Original uploads + processed derivatives

## 8. AI / LLM Architecture

### Provider Abstractions
```python
# packages/ai/providers/
├── base.py              # Abstract base classes
├── llm.py               # LLMProvider interface
├── vision.py            # VisionProvider interface
├── embeddings.py        # EmbeddingProvider interface
├── reranker.py          # RerankerProvider interface
├── router.py            # ModelRouter for capability-based selection
├── ollama.py            # Ollama implementation
└── openai_compatible.py # OpenAI-compatible implementation
```

### Capabilities
- `reasoning` - Complex problem solving
- `coding` - Code generation/analysis
- `summarization` - Text condensation
- `vision` - Image understanding
- `embeddings` - Vector representations
- `extraction` - Structured data extraction
- `classification` - Categorization tasks

## 9. Multimodal Pipeline

```
Input → Ingestion → Parsing → Extraction → Normalization → Chunking → Embedding → Index/Storage → Retrieval → Agents
```

### Supported Formats (Phase 1)
- Plain text / Markdown
- PDF (via pdfplumber/pymupdf)
- Images (via vision models)
- URLs (web fetching)

### Internal Representation
```python
class NormalizedDocument:
    content: str              # Extracted text
    metadata: DocumentMetadata
    chunks: List[Chunk]       # Semantic chunks
    images: List[ImageRef]    # Referenced images
    tables: List[Table]       # Extracted tables
```

## 10. Agent Architecture

### Framework Components
- `Agent` - Base class with lifecycle hooks
- `AgentContext` - Shared state, tools, memory
- `Tool` - Function calling abstraction
- `AgentRegistry` - Discovery and instantiation
- `Orchestrator` - Coordinates multi-agent workflows

### Initial Agents (MVP)
1. **PlannerAgent** - Decomposes research into tasks
2. **WebResearchAgent** - Searches and fetches web content
3. **DocumentAnalysisAgent** - Processes uploaded documents
4. **SynthesisAgent** - Combines evidence into findings
5. **ReportAgent** - Generates final structured report

## 11. Research Pipeline

```
User Request
    ↓
Request Analysis (intent, scope, constraints)
    ↓
Planner Agent → Research Plan (DAG of tasks)
    ↓
Task Execution (parallel where possible)
    ↓
Evidence Collection → Normalization → Storage
    ↓
Verification & Critique
    ↓
Synthesis → Report Generation
    ↓
Final Report + Execution Trace
```

## 12. API Design

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/research` | POST | Create new research job |
| `/api/research/{id}` | GET | Get research job status |
| `/api/research/{id}/plan` | GET | Get research plan |
| `/api/research/{id}/tasks` | GET | List tasks |
| `/api/research/{id}/sources` | GET | List collected sources |
| `/api/research/{id}/evidence` | GET | List evidence |
| `/api/research/{id}/report` | GET | Get final report |
| `/api/documents` | POST | Upload document |
| `/api/models` | GET | List available models |
| `/api/health` | GET | Health check |

## 13. Security & Privacy

- Environment variables for all secrets (`.env` not committed)
- Pydantic validation on all inputs
- File type/size validation on upload
- No arbitrary code execution from model output
- Tool permission boundaries
- Structured logging without secret leakage
- Rate limiting on API endpoints

## 14. Testing Strategy

| Test Type | Tools | Coverage |
|-----------|-------|----------|
| Unit | pytest | Core functions, schemas, utilities |
| Integration | pytest + testcontainers | DB, API, model providers |
| Agent | pytest + mocks | Agent behavior, tool use |
| Multimodal | pytest | Ingestion pipeline |
| E2E | pytest + httpx | Full research pipeline |
| AI Eval | Custom | Grounding, citations, hallucination |

## 15. Observability

- Request ID propagation
- Structured JSON logging (structlog)
- OpenTelemetry traces for agent execution
- Model call logging (prompt, response, tokens, latency)
- Research job state tracking
- Error tracking with context

## 16. Deployment & Infrastructure

### Development
```bash
docker-compose up -d  # PostgreSQL, ChromaDB, Redis, Ollama
cd apps/api && pip install -e .
cd apps/web && npm install && npm run dev
```

### Production Considerations
- Kubernetes deployment manifests
- Horizontal pod autoscaling
- Managed PostgreSQL/Redis
- S3-compatible file storage
- TLS termination
- Secrets management (Vault/SealedSecrets)

## 17. Development Phases

| Phase | Focus | Deliverables |
|-------|-------|--------------|
| 1 | Foundation | Repo, config, logging, basic API, frontend shell, tests |
| 2 | Research MVP | Planner, basic agents, evidence storage, synthesis, report |
| 3 | Multimodal | PDF, image, table ingestion, vision models |
| 4 | Agentic System | Specialized agents, orchestration, tools, critic |
| 5 | RAG/Knowledge | Embeddings, vector retrieval, grounding |
| 6 | Production | Auth, hardening, monitoring, CI/CD, deployment |

## 18. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Model hallucination | Evidence grounding, critic agent, citation requirements |
| Provider lock-in | Strict abstraction layer, multiple implementations |
| Scalability | Async architecture, task queue, horizontal scaling |
| Data quality | Validation at ingestion, verification agents |
| Cost (cloud models) | Local-first design, capability-based routing |

## 19. Model Provider Abstraction

The `ModelRouter` selects providers based on:
- Task capability requirements
- Model availability
- Cost/performance preferences
- Local vs cloud preference

```python
router.select_model(capabilities=["reasoning", "vision"], prefer_local=True)
```

## 20. Failure Handling

- **Model unavailable**: Fallback to alternative provider
- **Tool failure**: Retry with backoff, mark task failed, continue others
- **Parsing failure**: Log error, store raw content, continue
- **Timeout**: Configurable timeouts, partial result preservation
- **Partial completion**: Save progress, allow resume

---

*This blueprint documents the intended architecture. Implementation details may evolve.*