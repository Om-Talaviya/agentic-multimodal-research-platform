# Agent & Developer Operating Instructions: AGENTS.md

Welcome to the **Agentic Multimodal Research Platform** codebase. This file serves as the definitive, tool-agnostic operational guide for human developers and autonomous AI coding agents working in this repository.

---

## 1. System Architecture & High-Level Philosophy

The repository is organized as a modular Python monorepo with a decoupled FastAPI backend and a React (TypeScript + Vite) frontend.

### Architectural Tiers:
```
Frontend (React/Vite)
       │ HTTP / WebSocket
       ▼
FastAPI API Layer (apps/api)
       │
       ├── Auth & RBAC (JWT, PBKDF2, PostgreSQL/SQLite)
       ├── Research Pipeline Orchestrator (packages/research)
       │      │
       │      ├── PlannerAgent (packages/agents)
       │      ├── Task DAG Execution Engine (packages/research)
       │      ├── Specialized Agents (Web, Document, Critic, Report)
       │      │      └── Tool Registry (packages/tools)
       │      └── Hybrid RAG Layer (packages/retrieval)
       │
       └── AI Engine (packages/ai)
              └── ModelGateway
                     └── ModelRouter
                            ├── ModelRegistry (Task capability matching & model definitions)
                            └── ProviderRegistry (Ollama, Gemini, OpenAI-compatible)
```

---

## 2. Tech Stack Overview

| Domain | Technology | Key Libraries / Protocols |
|---|---|---|
| **Backend Framework** | Python 3.11+ / FastAPI | Pydantic v2 Settings, Structlog, Uvicorn |
| **Database & ORM** | PostgreSQL 16 / SQLite parity | SQLAlchemy 2.0 Async, Alembic migrations |
| **Vector Search & RAG** | ChromaDB / In-Memory | `rank-bm25`, Reciprocal Rank Fusion (RRF) |
| **Multimodal Ingestion** | Custom pipeline | `pdfplumber`, `python-docx`, `Pillow`, Vision LLMs |
| **AI Providers** | Multi-provider Gateway | Local Ollama, Official Google Gemini, OpenAI-compatible |
| **Frontend Framework** | React 18 / TypeScript | Vite, React Router v6, Lucide React, Vanilla CSS |
| **Testing** | pytest & pytest-asyncio | `httpx`, pytest-cov |

---

## 3. Directory Layout

```
.
├── apps/
│   ├── api/                     # FastAPI backend application
│   │   ├── src/
│   │   │   ├── api/             # Routes (auth, research, documents, models, health, ws)
│   │   │   ├── dependencies.py  # Dependency injection (Gateway, Repositories, EventBus)
│   │   │   └── main.py          # Application entry & CORS/middleware
│   │   └── tests/               # API route integration tests
│   └── web/                     # React frontend
│       ├── src/
│       │   ├── components/      # UI components (Layout, Badges, Tables)
│       │   ├── pages/           # Dashboard, NewResearch, ResearchDetail, Settings
│       │   ├── services/        # api.ts (HTTP client) and WebSocket helpers
│       │   └── types/           # TypeScript types (ResearchJob, Task, Evidence, Report)
│       └── package.json
│
├── packages/                    # Core modular Python packages
│   ├── ai/                      # Multi-provider Gateway, Router, Registry, Providers
│   ├── agents/                  # Autonomous agents (Planner, Web, Doc, Critic, Report)
│   ├── research/                # DAG execution, Pipeline, EventBus, Synthesis
│   ├── ingestion/               # Parsers (PDF, DOCX, Image, Text), Chunkers, Normalizers
│   ├── retrieval/               # Embedder, ChromaStore, InMemoryStore, BM25, Retriever
│   ├── database/                # SQLAlchemy async models, Repositories, Alembic
│   ├── tools/                   # Tool registry, WebSearch, SSRF-safe WebFetch, DocReader
│   └── shared/                  # Config, logging, JWT auth, security, exceptions
│
├── docs/                        # Architectural specs and diagrams
├── infrastructure/              # Kubernetes manifests, Docker Compose, monitoring
└── pyproject.toml               # Python monorepo configuration
```

---

## 4. Coding Conventions & Standards

### Python (Backend & Packages)
1. **Typing**: Use strict static typing across all packages (`typing.Optional`, `Union`, `List`, `Dict`, `Tuple`, or modern `|` syntax). Ensure all functions have parameter and return type hints.
2. **Pydantic**: Use Pydantic v2 schemas (`BaseModel`, `Field`, `model_dump()`, `model_copy()`).
3. **Async / Await**: All database interactions (`AsyncSession`), model inferences, HTTP queries (`httpx.AsyncClient`), and tool runs MUST be async. Never block the event loop.
4. **Error Handling**: Use domain exceptions defined in `shared.exceptions` (e.g., `ModelNotFoundError`, `ProviderUnavailableError`, `AuthenticationError`, `ValidationError`).
5. **Logging**: Always use structured logging with `structlog` (`logger = get_logger(__name__)`). Include contextual key-value pairs (e.g., `job_id`, `task_id`, `model`, `latency_ms`). Do not use `print()` in production packages.
6. **SQL Parity**: Database models must remain cross-compatible with PostgreSQL (using `JSONB` and native `UUID`) and SQLite (fallback variants via `JSON().with_variant(...)`).

### TypeScript / React (Frontend)
1. **Vanilla CSS**: Rely on the established design system tokens in `apps/web/src/index.css`. Avoid adding Tailwind CSS unless explicitly requested.
2. **State Management**: Keep components focused. Handle loading, error, and empty states explicitly.
3. **Resilient WebSockets**: Maintain exponential backoff auto-reconnect logic and support token authentication via query parameters or Authorization headers.

---

## 5. Development & Testing Commands

Run commands from the repository root or relevant project subdirectories:

```bash
# 1. Run all unit tests across all packages
pytest packages/ apps/api/tests/ -v

# 2. Run specific package tests
pytest packages/ai/tests/ -v
pytest packages/research/tests/ -v
pytest packages/ingestion/tests/ -v
pytest packages/database/tests/ -v

# 3. Apply database migrations
cd apps/api
alembic upgrade head

# 4. Start backend development server
uvicorn src.main:app --reload --port 8000

# 5. Build and validate frontend
cd apps/web
npm install
npm run build
npm run lint
```

---

## 6. Critical Constraints & Known Pitfalls

1. **Security & Secrets**: NEVER hardcode API keys, passwords, or JWT secrets in code or documentation. Always reference environment variables by name (e.g., `GEMINI_API_KEY`, `OPENAI_API_KEY`, `DATABASE_URL`, `SECRET_KEY`).
2. **SSRF Prevention**: When fetching web resources, always route through `WebFetchTool` or validate targets against `packages.shared.security.is_safe_url()`. Private IPs, loopbacks, and metadata service endpoints (e.g., `169.254.169.254`) must be rejected.
3. **Model Provider Migration**: Note that the legacy unofficial `GeminiWeb2API` has been removed in Phase 7.3 in favor of the official Google Gemini SDK (`ai.providers.gemini.GeminiProvider`). Do NOT restore or reintroduce Web2API scrapers.
4. **WebSocket Connection Lifecycles**: Always subscribe to the `ResearchEventBus` BEFORE querying initial snapshot state to prevent race conditions during rapid background task transitions.
5. **Windows Path Compatibility**: Use forward slashes (`/`) or `pathlib.Path` in Python code. Avoid hardcoding Unix-only shell commands or symlinks that break on Windows systems.

---

## 7. Git & Branching Rules

- Work on feature branches or version branches (e.g., `develop/v1.1`).
- Write descriptive commit messages adhering to conventional commits (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`).
- **DO NOT commit or push without explicit user request.**

---

## 8. Current Project Phase Status

- **Phase 1 (Foundation)**: 🟢 COMPLETE
- **Phase 2 (Research MVP)**: 🟢 COMPLETE
- **Phase 3 (Multimodal Ingestion)**: 🟢 COMPLETE
- **Phase 4 (Agentic System)**: 🟢 COMPLETE
- **Phase 5 (RAG / Knowledge Layer)**: 🟢 COMPLETE
- **Phase 6 (Production & Security)**: 🟢 COMPLETE
- **Phase 7.1 (Dashboard UI Fix)**: 🟢 COMPLETE
- **Phase 7.2 (Persistent Database Users)**: 🟢 COMPLETE
- **Phase 7.3 (Official Gemini Provider)**: 🟢 COMPLETE
- **Phase 8A (Intelligent Model Routing Core)**: 🟢 COMPLETE (`ModelRegistry`, `ModelRouter`, `ModelGateway`)
- **Phase 8B (Quotas, Usage Tracking & Fallback Extensions)**: 🟡 IN PROGRESS / UNCOMMITTED (Implementation exists locally, awaiting final review and integration).
