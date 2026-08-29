# Architecture Documentation

## High-Level Architecture

The Agentic Multimodal Research Platform follows a modular, layered architecture with clear separation of concerns:

```
┌────────────────────────────────────────────────────────────────────┐
│                         Presentation Layer                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│  │   Web UI    │  │   REST API  │  │  WebSocket  │                │
│  │  (React)    │  │  (FastAPI)  │  │  (Real-time)│                │
│  └─────────────┘  └─────────────┘  └─────────────┘                │
└────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────────┐
│                       Application Layer                            │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                  Research Orchestrator                       │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐  │  │
│  │  │ Planner  │ │ Research │ │ Evidence │ │  Synthesis &   │  │  │
│  │  │ Agent    │ │ Agents   │ │ Agents   │ │  Report Agents │  │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────────────┘  │  │
│  └─────────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                    Model Router                              │  │
│  │  ┌─────────┐ ┌──────────┐ ┌───────────┐ ┌──────────────┐   │  │
│  │  │  LLM    │ │ Vision   │ │ Embedding │ │  Reranker    │   │  │
│  │  │Provider │ │ Provider │ │ Provider  │ │  Provider    │   │  │
│  │  └─────────┘ └──────────┘ └───────────┘ └──────────────┘   │  │
│  └─────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────────┐
│                         Data Layer                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ PostgreSQL   │  │  ChromaDB    │  │  File Store  │             │
│  │ (Relational) │  │  (Vectors)   │  │  (Assets)    │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└────────────────────────────────────────────────────────────────────┘
```

## Core Design Principles

### 1. Dependency Inversion
All high-level modules depend on abstractions, not concrete implementations:
- `LLMProvider` interface → `OllamaProvider`, `OpenAICompatibleProvider`
- `VectorStore` interface → `ChromaStore`, future `PineconeStore`, `WeaviateStore`
- `DocumentParser` interface → `PDFParser`, `ImageParser`, `TextParser`

### 2. Configuration-Driven Behavior
Behavior controlled via Pydantic Settings from environment variables:
- Model selection and parameters
- Database connections
- Feature flags
- Resource limits

### 3. Async-First Design
All I/O operations use async/await:
- FastAPI endpoints
- Database operations (SQLAlchemy async)
- Model provider calls
- File operations
- HTTP requests

### 4. Structured Logging & Observability
- Every request gets a `request_id`
- Every research job gets a `job_id`
- Every agent run gets a `run_id`
- All logs are structured JSON with context
- OpenTelemetry traces span agent executions

## Package Boundaries

### `packages/ai` - Model Provider Abstractions
```
ai/
├── providers/
│   ├── base.py              # Abstract base classes
│   ├── llm.py               # LLMProvider protocol
│   ├── vision.py            # VisionProvider protocol
│   ├── embeddings.py        # EmbeddingProvider protocol
│   ├── reranker.py          # RerankerProvider protocol
│   ├── router.py            # ModelRouter
│   ├── ollama.py            # Ollama implementation
│   └── openai_compatible.py # OpenAI-compatible implementation
├── schemas.py               # Request/response models
├── exceptions.py            # Provider-specific exceptions
└── __init__.py
```

### `packages/agents` - Agent Framework
```
agents/
├── base.py                  # Agent base class, AgentContext
├── registry.py              # AgentRegistry for discovery
├── orchestrator.py          # Multi-agent coordination
├── tools/
│   ├── base.py              # Tool protocol
│   ├── registry.py          # ToolRegistry
│   └── builtin/             # Built-in tools (search, fetch, etc.)
├── memory.py                # Agent memory (short/long term)
├── planner/
│   └── planner_agent.py     # Planning agent implementation
├── research/
│   ├── web_agent.py         # Web research agent
│   └── document_agent.py    # Document analysis agent
├── synthesis/
│   └── synthesis_agent.py   # Evidence synthesis agent
├── report/
│   └── report_agent.py      # Report generation agent
└── __init__.py
```

### `packages/research` - Research Pipeline
```
research/
├── pipeline.py              # Main pipeline orchestration
├── planner.py               # Research planning logic
├── models.py                # Research job, task, plan models
├── evidence.py              # Evidence collection & verification
├── synthesis.py             # Finding synthesis
├── report.py                # Report generation
└── __init__.py
```

### `packages/ingestion` - Multimodal Ingestion
```
ingestion/
├── pipeline.py              # Ingestion pipeline orchestrator
├── parsers/
│   ├── base.py              # DocumentParser protocol
│   ├── text.py              # Text/markdown parser
│   ├── pdf.py               # PDF parser (pdfplumber)
│   ├── image.py             # Image parser (vision model)
│   └── docx.py              # DOCX parser
├── extractors/
│   ├── text.py              # Text extraction
│   ├── tables.py            # Table extraction
│   └── metadata.py          # Metadata extraction
├── chunking.py              # Semantic chunking strategies
├── normalization.py         # Normalized document representation
└── __init__.py
```

### `packages/retrieval` - Vector Search & RAG
```
retrieval/
├── vector_store.py          # VectorStore protocol
├── chroma_store.py          # ChromaDB implementation
├── embedder.py              # Embedding generation
├── retriever.py             # Hybrid retrieval (vector + keyword)
├── reranker.py              # Result reranking
└── __init__.py
```

### `packages/database` - Database Abstractions
```
database/
├── connection.py            # Async engine/session management
├── models/                  # SQLAlchemy models
│   ├── research_job.py
│   ├── research_task.py
│   ├── source.py
│   ├── evidence.py
│   ├── report.py
│   └── agent_run.py
├── repositories/            # Repository pattern
│   ├── research_job_repo.py
│   ├── source_repo.py
│   └── evidence_repo.py
├── migrations/              # Alembic migrations
└── __init__.py
```

### `packages/tools` - Tool System
```
tools/
├── base.py                  # Tool protocol
├── registry.py              # ToolRegistry
├── definitions/             # Tool schemas
│   ├── web_search.py
│   ├── web_fetch.py
│   ├── document_read.py
│   └── code_exec.py         # Sandboxed (future)
└── __init__.py
```

### `packages/shared` - Common Utilities
```
shared/
├── config.py                # Shared configuration
├── logging.py               # Structured logging setup
├── observability.py         # OpenTelemetry setup
├── exceptions.py            # Custom exceptions
├── types.py                 # Common type definitions
├── utils.py                 # Utility functions
└── __init__.py
```

## Data Flow: Research Request

```
1. POST /api/research
   │
   ▼
2. ResearchOrchestrator.create_job()
   │   - Creates ResearchJob in DB
   │   - Emits JobCreated event
   │
   ▼
3. PlannerAgent.analyze_request()
   │   - Uses LLM to decompose request
   │   - Produces ResearchPlan (DAG of tasks)
   │   - Stores plan in DB
   │
   ▼
4. Orchestrator.execute_plan()
   │   - Topological sort of tasks
   │   - Parallel execution where possible
   │   - Each task → Agent.run()
   │
   ▼
5. Agent Execution Loop
   │   - Agent receives Task + Context
   │   - Agent uses Tools + Model Providers
   │   - Agent produces Evidence/Results
   │   - Results stored in DB
   │   - Execution trace logged
   │
   ▼
6. Evidence Verification
   │   - Cross-reference sources
   │   - Detect contradictions
   │   - Assess credibility
   │
   ▼
7. SynthesisAgent.synthesize()
   │   - Groups evidence by claim
   │   - Identifies consensus/conflicts
   │   - Produces Findings with citations
   │
   ▼
8. ReportAgent.generate()
   │   - Structures findings
   │   - Adds uncertainty markers
   │   - Generates citations
   │   - Produces final report
   │
   ▼
9. GET /api/research/{id}/report
```

## Concurrency Model

- **Research Jobs**: Independent, can run in parallel
- **Tasks within Job**: DAG-based, parallel where dependencies allow
- **Agent Execution**: Single-threaded per agent instance (stateful)
- **Model Calls**: Async, concurrent via connection pooling
- **Database**: Async connection pool (SQLAlchemy async)

## Error Handling Strategy

```python
# Layered error handling
try:
    result = await agent.run(task, context)
except ModelProviderError as e:
    # Log, try fallback provider, or mark task failed
    await handle_model_failure(task, e)
except ToolError as e:
    # Retry with backoff, then fail task
    await handle_tool_failure(task, e)
except ValidationError as e:
    # Invalid input, fail fast
    raise
except Exception as e:
    # Unexpected: log full trace, mark job errored
    logger.exception("Unexpected error", job_id=job.id)
    await mark_job_failed(job.id, str(e))
```

## Security Boundaries

```
┌─────────────────────────────────────────────┐
│                 Trusted Zone                │
│  ┌─────────┐ ┌─────────┐ ┌───────────────┐ │
│  │ Orchest.│ │ Agents  │ │ Model Router  │ │
│  └─────────┘ └─────────┘ └───────────────┘ │
└─────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌───────────────┐       ┌───────────────┐
│  Tools        │       │ Model         │
│  (Sandboxed)  │       │ Providers     │
│               │       │ (External)    │
│ - Web search  │       │               │
│ - File read   │       │ - Ollama      │
│ - Code exec   │       │ - OpenAI      │
│   (isolated)  │       │ - Anthropic   │
└───────────────┘       └───────────────┘
```

- Tools execute in restricted contexts
- Model providers are external dependencies
- No `eval()` or arbitrary code execution from model output
- File system access limited to designated directories

## Extensibility Points

1. **New Model Provider**: Implement `LLMProvider` protocol
2. **New Agent**: Subclass `Agent`, register in `AgentRegistry`
3. **New Tool**: Implement `Tool` protocol, register in `ToolRegistry`
4. **New Document Format**: Implement `DocumentParser` protocol
5. **New Vector Store**: Implement `VectorStore` protocol
6. **New Retrieval Strategy**: Extend `Retriever` class

## Configuration Management

All configuration via `packages/shared/config.py` using Pydantic Settings:

```python
class Settings(BaseSettings):
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Database
    database_url: str
    database_pool_size: int = 10
    
    # Vector Store
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    
    # Redis
    redis_url: str
    
    # Model Providers
    ollama_base_url: str = "http://localhost:11434"
    default_llm_model: str = "llama3.1"
    default_embedding_model: str = "nomic-embed-text"
    
    # File Storage
    upload_dir: Path = Path("./uploads")
    max_upload_size: int = 50 * 1024 * 1024  # 50MB
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
```

---

*Architecture is a living document. Update as implementation evolves.*