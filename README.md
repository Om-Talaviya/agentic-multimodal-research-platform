# Agentic Multimodal Research Platform

<p align="left">
  <a href="https://github.com/Om-Talaviya"><img src="https://img.shields.io/badge/Architect-Om%20Talaviya-38bdf8?style=flat-square&logo=github&logoColor=white" alt="Author" /></a>
  <img src="https://img.shields.io/badge/Python-3.11+-3776ab?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Framework-FastAPI%20%26%20LangGraph-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Modality-Multimodal%20RAG-7c3aed?style=flat-square" alt="Multimodal" />
</p>

A production-grade, local-first research platform that uses agentic AI to conduct autonomous, verifiable, and evidence-grounded research across multiple modalities (text, PDF, DOCX, images, and the live web).

---

## Architecture Overview

![System Architecture](docs/architecture.png)

The platform implements a layered, decoupled architecture with a dynamic Directed Acyclic Graph (DAG) task execution pipeline, structured agentic orchestration, hybrid vector/BM25 retrieval (RAG), and a centralized multi-provider model routing layer.

---

## Core Capabilities

- **Autonomous Agentic Pipeline**: Dynamic Planner → Parallel Specialized Research Agents → Critic/Verifier → Evidence Synthesis → Structured Report Generation.
- **Dynamic DAG Task Execution**: Tasks with dependency graphs are scheduled and executed concurrently with real-time topological resolution and error recovery.
- **Multimodal Ingestion**: Native extraction and chunking for Plain Text, Markdown, PDF (with tables via `pdfplumber`), DOCX (`python-docx`), and Images (via Vision models).
- **Intelligent Model Routing & Gateway**: Centralized `ModelGateway` → `ModelRouter` → `ModelRegistry` / `ProviderRegistry` hierarchy with task-to-model matching, automated fallback failovers, and telemetry capture.
- **Hybrid RAG & Grounded Evidence**: Vector embeddings (ChromaDB / In-Memory) combined with BM25 sparse lexical search and Reciprocal Rank Fusion (RRF) for strict citation preservation.
- **Live Real-time Streaming**: Bi-directional WebSocket streaming (`/api/v1/research/{id}/ws`) delivering real-time task lifecycle events, DAG transitions, evidence extraction, and report streaming.
- **Persistent RBAC Authentication**: PostgreSQL-backed user store with Alembic migrations, PBKDF2-HMAC-SHA256 password hashing, and JWT access/refresh token lifecycle.
- **Production Hardening & Observability**: Server-Side Request Forgery (SSRF) protection on web tools, prompt injection detection, Prometheus metrics (`/metrics`), structured `structlog` logging, and Kubernetes deployment manifests.

---

## Tech Stack

### Backend & AI Engine
- **Framework**: FastAPI (Python 3.11+) with Uvicorn ASGI
- **Database**: PostgreSQL 16 (production) / SQLite (development/testing) with SQLAlchemy 2.0 Async + Alembic migrations
- **Vector & Cache**: ChromaDB 0.4+, Redis 7 (caching and event pub/sub)
- **Model Providers**: Ollama (local-first `llama3.1`, `llava`, `nomic-embed-text`), Google Gemini API (`gemini-2.0-flash`), OpenAI-compatible endpoints
- **Data Ingestion**: `pdfplumber`, `python-docx`, `Pillow`, `rank-bm25`
- **Security & Auth**: `python-jose` (JWT), `passlib` / `hashlib` PBKDF2, IPv4/IPv6 private IP filtering

### Frontend
- **Framework**: React 18 with TypeScript and Vite
- **Styling**: Vanilla CSS with modern tokens, CSS variables, and glassmorphism styling
- **Routing & Icons**: React Router v6, Lucide React
- **Network**: Axios HTTP client and native WebSocket client with exponential backoff auto-reconnect

---

## Repository Structure

```
.
├── apps/
│   ├── api/                     # FastAPI backend application
│   │   ├── src/
│   │   │   ├── api/             # HTTP routes, dependencies & WebSockets
│   │   │   └── main.py          # ASGI application entry point
│   │   └── tests/               # API route and integration tests
│   └── web/                     # React + TypeScript + Vite frontend
│       ├── src/
│       │   ├── components/      # Reusable UI components
│       │   ├── pages/           # Dashboard, NewResearch, ResearchDetail, Settings
│       │   ├── services/        # API and WebSocket client adapters
│       │   └── types/           # TypeScript domain definitions
│       └── package.json
│
├── packages/                    # Modular Python shared packages
│   ├── ai/                      # ModelRegistry, ProviderRegistry, ModelRouter, ModelGateway
│   ├── agents/                  # PlannerAgent, WebAgent, DocumentAgent, CriticAgent, ReportAgent
│   ├── research/                # Pipeline orchestrator, DAG runner, event bus, synthesis
│   ├── ingestion/               # Document parsers (PDF, DOCX, Image, Text), chunkers, extractors
│   ├── retrieval/               # Embedder, ChromaStore, InMemoryStore, BM25, HybridRetriever
│   ├── database/                # SQLAlchemy async models, repositories, Alembic migrations
│   ├── tools/                   # Tool registry, WebSearch, WebFetch (SSRF safe), DocReader
│   └── shared/                  # Config, structlog, JWT auth, security filters, exceptions
│
├── docs/                        # Deep-dive architectural specifications & diagrams
├── infrastructure/              # Docker Compose, Kubernetes manifests, Prometheus configs
├── pyproject.toml               # Workspace root configuration
└── docker-compose.yml           # Local multi-service infrastructure
```

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 20+
- Ollama (optional, for local model inference)

### 1. Configure Environment
```bash
cp .env.example .env
# Edit .env if configuring external API keys or custom ports
```

### 2. Launch Local Infrastructure
```bash
docker-compose up -d
```
Starts:
- PostgreSQL (`localhost:5432`)
- ChromaDB (`localhost:8000`)
- Redis (`localhost:6379`)
- Ollama (`localhost:11434`)

*(Optional) Pull local Ollama models:*
```bash
docker exec -it ollama ollama pull llama3.1
docker exec -it ollama ollama pull llava
docker exec -it ollama ollama pull nomic-embed-text
```

### 3. Backend Setup
```bash
cd apps/api
pip install -e ".[dev]"

# Apply database migrations
alembic upgrade head

# Start FastAPI development server
uvicorn src.main:app --reload --port 8000
```
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/v1/health`
- Metrics: `http://localhost:8000/metrics`

### 4. Frontend Setup
```bash
cd apps/web
npm install
npm run dev
```
- Web Application: `http://localhost:5173`

---

## Development & Testing Commands

### Backend Test Suite
```bash
# Run all unit tests across all packages
pytest packages/ apps/api/tests/ -v

# Run backend API integration tests
pytest apps/api/tests/ -v

# Run with coverage report
pytest --cov=packages --cov=apps/api
```

### Frontend Validation
```bash
cd apps/web
npm run build
npm run lint
```

### Code Formatting & Linting
```bash
# Ruff lint & formatting
ruff check .
ruff format .

# Type checking
mypy apps/api/src packages/
```

---

## API Summary

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/v1/auth/login` | Authenticate and obtain JWT access/refresh tokens | No |
| `POST` | `/api/v1/auth/token/refresh` | Exchange refresh token for fresh access token | No |
| `GET` | `/api/v1/auth/me` | Retrieve authenticated user profile and permissions | Yes |
| `GET` | `/api/v1/health` | Service and gateway health probe | No |
| `POST` | `/api/v1/research` | Create and trigger an autonomous research job | Yes (`research:create`) |
| `GET` | `/api/v1/research` | List research jobs with pagination | Yes (`research:read`) |
| `GET` | `/api/v1/research/{id}` | Get research job metadata and execution status | Yes (`research:read`) |
| `GET` | `/api/v1/research/{id}/tasks` | Get DAG task graph and execution progress | Yes (`research:read`) |
| `GET` | `/api/v1/research/{id}/sources` | List retrieved web and document sources | Yes (`research:read`) |
| `GET` | `/api/v1/research/{id}/evidence` | List extracted claims and verification confidence | Yes (`research:read`) |
| `GET` | `/api/v1/research/{id}/report` | Retrieve final synthesized research report | Yes (`research:read`) |
| `WS` | `/api/v1/research/{id}/ws` | Live WebSocket streaming for DAG updates & events | Yes (Token query/header) |
| `POST` | `/api/v1/documents` | Ingest and parse PDF, DOCX, or image document | Yes (`documents:upload`) |
| `GET` | `/api/v1/models` | List catalog models and provider health statuses | No |
| `GET` | `/metrics` | Prometheus telemetry and metrics exposition | No / Internal |

---

## Project Status

| Phase | Milestone | Status | Notes |
|---|---|---|---|
| **Phase 1** | Foundation | 🟢 COMPLETE | Backend shell, async DB, logging, React frontend |
| **Phase 2** | Research MVP | 🟢 COMPLETE | DAG runner, Planner, Web/Doc/Report agents, WebSockets |
| **Phase 3** | Multimodal Ingestion | 🟢 COMPLETE | PDF (`pdfplumber`), DOCX, Vision images, semantic chunking |
| **Phase 4** | Agentic System | 🟢 COMPLETE | SSRF-hardened tools, Critic agent, memory, tracing |
| **Phase 5** | RAG / Knowledge Layer | 🟢 COMPLETE | Hybrid RRF (Vector + BM25), Embedder, citation preservation |
| **Phase 6** | Production & Security | 🟢 COMPLETE | JWT auth, RBAC, Prometheus metrics, K8s manifests |
| **Phase 7.1** | Dashboard Integration | 🟢 COMPLETE | Fixed job response mapping in web dashboard |
| **Phase 7.2** | Persistent Users | 🟢 COMPLETE | PostgreSQL `users` table, Alembic migrations, password hashing |
| **Phase 7.3** | Official Gemini Provider | 🟢 COMPLETE | Migrated to official Gemini API; removed unofficial Web2API |
| **Phase 8A** | Intelligent Model Routing Core | 🟢 COMPLETE | `ModelRegistry`, `ProviderRegistry`, `ModelRouter`, `ModelGateway` |
| **Phase 8B** | Quotas, Usage Telemetry & Fallback Refinements | 🟡 IN REVIEW | Implementation completed in local branch; uncommitted / pending review |

---

## Security & Architectural Guarantees

1. **Local-First Privacy**: Can operate in 100% offline air-gapped mode using Ollama without cloud leakage.
2. **SSRF Protection**: `WebFetchTool` validates all resolved IP addresses, rejecting Loopback (`127.0.0.0/8`, `::1`), Private subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `fc00::/7`), Link-local (`169.254.0.0/16`, `fe80::/10`), and Multicast.
3. **No Unchecked Model Execution**: Models generate data and structured payloads; no arbitrary string evaluation (`eval()`) is executed.