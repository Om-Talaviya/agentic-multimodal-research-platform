# Agentic Multimodal Research Platform

<p align="left">
  <a href="https://github.com/Om-Talaviya"><img src="https://img.shields.io/badge/Architect-Om%20Talaviya-38bdf8?style=flat-square&logo=github&logoColor=white" alt="Author" /></a>
  <img src="https://img.shields.io/badge/Python-3.11+-3776ab?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Framework-FastAPI%20%26%20LangGraph-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Modality-Multimodal%20RAG-7c3aed?style=flat-square" alt="Multimodal" />
  <img src="https://img.shields.io/badge/Status-Phase%2010%20Complete-success?style=flat-square" alt="Status" />
  <img src="https://img.shields.io/badge/Branch-develop%2Fv1.1-blue?style=flat-square" alt="Branch" />
</p>

An enterprise-grade, local-first **AI Research Operating System** that conducts autonomous, verifiable, and evidence-grounded investigations across multiple modalities (text, academic PDFs, DOCX, datasets, images, and the live web).

> **This isn't just a chatbot.**  
> The platform enables AI to **Plan $\rightarrow$ Investigate $\rightarrow$ Retrieve $\rightarrow$ Reason $\rightarrow$ Critique $\rightarrow$ Synthesize $\rightarrow$ Report**, while managing multi-user authentication, quota allocation, multi-provider model routing, persistent storage, and real-time streaming progress.

---

## High-Level System Architecture

```
                                 ┌──────────────┐
                                 │     USER     │
                                 └───────┬──────┘
                                         │
                                         ▼
                        ┌─────────────────────────────────┐
                        │      React Web Platform         │
                        │ (Dashboard / Research / Studio) │
                        └────────────────┬────────────────┘
                                         │ HTTP / WebSocket
                                         ▼
                        ┌─────────────────────────────────┐
                        │          FastAPI API            │
                        └────────┬───────────────┬────────┘
                                 │               │
                 ┌───────────────┘               └───────────────┐
                 ▼                                               ▼
      ┌─────────────────────┐                         ┌─────────────────────┐
      │   Research Engine   │                         │   Knowledge Layer   │
      │ (Agent Orchestrator)│                         │  (Hybrid RAG Store) │
      └──────────┬──────────┘                         └──────────┬──────────┘
                 │                                               │
        ┌────────┴───────────────────┐                           │
        ▼              ▼             ▼                           │
   ┌─────────┐   ┌───────────┐ ┌──────────┐                      │
   │ Planner │   │ Web Agent │ │Doc Agent │                      │
   └────┬────┘   └─────┬─────┘ └────┬─────┘                      │
        │              │            │                            │
        └──────────────┼────────────┴────────────────────────────┤
                       ▼                                         │
                 ┌───────────┐                                   │
                 │  Critic   │◄──────────────────────────────────┘
                 └─────┬─────┘
                       ▼
                 ┌───────────┐
                 │ Synthesis │
                 └─────┬─────┘
                       ▼
                 ┌───────────┐
                 │  Report   │
                 └───────────┘

═════════════════════════════════════════════════════════════════════════════════
                              PLATFORM INFRASTRUCTURE
─────────────────────────────────────────────────────────────────────────────────
  [Authentication]       [AI Infrastructure]              [Platform Persistence]
  • Users & RBAC         • ModelRegistry (Capabilities)   • PostgreSQL / SQLite
  • PBKDF2 Password Hash • ModelRouter (Task Matching)    • ChromaDB / In-Memory
  • JWT Access/Refresh   • ModelGateway (Failover)        • Usage Records & Quotas
  • User Context Flow    • Ollama / Gemini / OpenAI       • Row-Locking Concurrency
═════════════════════════════════════════════════════════════════════════════════
```

---

## What Makes This Platform Different?

| Feature | Generic AI Chatbot / Wrapper | Agentic Multimodal Research Platform |
|---|---|---|
| **Execution Paradigm** | Single-prompt `Question $\rightarrow$ LLM $\rightarrow$ Answer` | Multi-agent DAG `Plan $\rightarrow$ Search $\rightarrow$ Read $\rightarrow$ Critique $\rightarrow$ Synthesize` |
| **Model Coupling** | Locked to a single proprietary API | **Model-Agnostic Routing**: Dynamically routes tasks to optimal fast, vision, or reasoning models with automated failover |
| **Evidence & Provenance** | Unverifiable assertions & frequent hallucinations | **Strict Claim $\rightarrow$ Evidence Mapping**: Every claim links to verified sources, document page numbers, and confidence metrics |
| **Critic & Verification** | No verification loop | Independent `CriticAgent` detects contradictions, audits sufficiency, and triggers iterative research loops |
| **Data Ingestion** | Raw text only | Native extraction for multi-page PDFs with tables, DOCX, images, and tabular datasets |
| **Multi-Tenancy & Quotas** | Simple API keys or no quotas | Persistent RBAC, transactional row-locking token/cost quotas, and per-user usage attribution |

---

## Current Status & Evolution

The project is currently at **Phase 10 Complete** on the stable branch `develop/v1.1`.

```
Phase 1: Foundation                  [████████████████████] 100%
Phase 2: Research MVP                [████████████████████] 100%
Phase 3: Multimodal Ingestion        [████████████████████] 100%
Phase 4: Agentic System              [████████████████████] 100%
Phase 5: RAG / Knowledge Core        [████████████████████] 100%
Phase 6: Production / Security       [████████████████████] 100%
Phase 7: Application Maturity        [████████████████████] 100%
Phase 8A: Intelligent Model Routing  [████████████████████] 100% (Commit: 88ac57d)
Phase 8B: Usage Tracking & Quotas    [████████████████████] 100% (Commit: a603114)
Phase 9: Intelligent Knowledge Auto  [████████████████████] 100%
Phase 10: Evidence & Citation Intel  [████████████████████] 100%
─────────────────────────────────────────────────────────────────────────────────
Phase 11: Advanced Research Planning [░░░░░░░░░░░░░░░░░░░░] NEXT MILESTONE
```

---

## 6-Generation Product Roadmap (Phases 9 – 26)

### Generation 1: Intelligent Research Core
- **Phase 9: Intelligent Knowledge Automation (COMPLETE)**: Automated end-to-end ingestion (`Upload $\rightarrow$ Validate $\rightarrow$ Extract $\rightarrow$ Normalize $\rightarrow$ Chunk $\rightarrow$ Embed $\rightarrow$ Index`) and autonomous planner retrieval integration.
- **Phase 10: Evidence & Citation Intelligence (COMPLETE)**: Strict source tracking, claim-to-evidence links, coordinate anchoring (`page_number`, `paragraph_index`, table coordinates), reliability metrics, and pairwise contradiction detection.
- **Phase 11: Advanced Research Planning (NEXT)**: Deep query decomposition into multi-tier subquestions with agent role specialization.

### Generation 2: Multimodal Intelligence
- **Phase 12: Advanced Multimodal Research**: Unified context across 50+ page PDFs, research papers, images, charts, graphs, tables, audio, and video.
- **Phase 13: Dataset & Data Analysis Intelligence**: Tabular data processing (CSV, Excel, JSON, SQL) with deterministic computational tools and charting.
- **Phase 14: Document & Paper Intelligence**: Deep academic paper structure parsing (sections, tables, figures, citations, limitations, methodology diffs).

### Generation 3: Autonomous Research
- **Phase 15: Deep Research Engine**: Autonomous recursive research loops (`Critic identifies gap $\rightarrow$ Planner schedules subtask $\rightarrow$ Synthesizer updates report`).
- **Phase 16: Research Memory**: Persistent cross-session research memory allowing users to resume complex investigations months later.
- **Phase 17: Long-Term Knowledge Graph**: Entity-relationship graphs connecting researchers, claims, technologies, datasets, and concepts beyond vector search.

### Generation 4: Collaboration Platform
- **Phase 18: Projects & Workspaces**: Multi-tiered workspace organization (`User $\rightarrow$ Workspace $\rightarrow$ Projects $\rightarrow$ Knowledge & Research`).
- **Phase 19: Team Collaboration**: Workspace role-based sharing (Owner, Researcher, Analyst, Reviewer, Viewer), inline comments, and collaborative reports.

### Generation 5: AI Platform Intelligence
- **Phase 20: Intelligent Model Ecosystem**: Multi-variable routing optimization (Task, Quality, Latency, Cost budget, Context size, Provider health, Quotas).
- **Phase 21: Model Evaluation System**: Automated benchmarking for accuracy, relevance, latency, cost, and reasoning quality.
- **Phase 22: Agent Evaluation**: Observability framework tracking research quality, evidence coverage, hallucination rate, and execution efficiency.

### Generation 6: Production Product
- **Phase 23: Enterprise Security**: SOC 2 & GDPR compliance, workspace isolation, immutable audit logging, data retention policies, and secret management.
- **Phase 24: Production Infrastructure**: Distributed task queues (Celery/Redis), worker pools, object storage (S3/MinIO), autoscaling, and DB replication.
- **Phase 25: Public API & Developer Platform**: Public developer REST endpoints (`POST /research`, `POST /documents`), client SDKs, and API key management.
- **Phase 26: Research Automation**: Scheduled recurring research sweeps, topic monitoring, diff detection, and automated alerting.

---

## Tech Stack

| Domain | Technologies |
|---|---|
| **Backend & ASGI** | Python 3.11+, FastAPI, Uvicorn, Pydantic v2, Structlog |
| **Database & ORM** | PostgreSQL 16 (production) / SQLite (testing), SQLAlchemy 2.0 Async, Alembic |
| **Vector & RAG** | ChromaDB, In-Memory Vector Store, `rank-bm25` (Sparse Search), Reciprocal Rank Fusion (RRF) |
| **Multimodal Ingestion**| `pdfplumber`, `python-docx`, `Pillow`, Vision LLMs |
| **AI Providers** | Multi-provider Gateway: Local Ollama, Official Google Gemini SDK, OpenAI-compatible |
| **Frontend** | React 18, TypeScript, Vite, React Router v6, Lucide React, Modern Vanilla CSS |
| **Security & Auth** | PBKDF2-HMAC-SHA256, JWT (Access + Refresh), SSRF-safe URL validation, Prompt Injection Guards |

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
├── design/                      # UI/UX design architecture, tokens, and wireframe specs
├── docs/                        # Deep-dive architectural specifications, PRD, TRD, flows, schema
├── infrastructure/              # Docker Compose, Kubernetes manifests, Prometheus configs
└── pyproject.toml               # Monorepo workspace configuration
```

---

## Quick Start

### 1. Configure Environment
```bash
cp .env.example .env
# Configure GEMINI_API_KEY or local Ollama endpoints as needed
```

### 2. Launch Local Infrastructure
```bash
docker-compose up -d
```
Starts PostgreSQL (`5432`), ChromaDB (`8000`), Redis (`6379`), and Ollama (`11434`).

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

### 4. Frontend Setup
```bash
cd apps/web
npm install
npm run dev
```
- Web Application: `http://localhost:5173`

---

## Development & Testing Commands

```bash
# Run all unit tests across all packages
pytest packages/ apps/api/tests/ -v

# Run specific package tests
pytest packages/ai/tests/ -v
pytest packages/research/tests/ -v
pytest packages/database/tests/ -v

# Run with coverage report
pytest --cov=packages --cov=apps/api

# Frontend build and linting
cd apps/web
npm run build
npm run lint
```

---

## Security & Architectural Guarantees

1. **Local-First Privacy**: Can run 100% air-gapped using Ollama without sending sensitive data to external APIs.
2. **SSRF Protection**: `WebFetchTool` validates all resolved IP addresses, strictly blocking loopback, private subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), link-local metadata endpoints (`169.254.169.254`), and multicast ranges.
3. **Deterministic Calculations**: Agents utilize code execution/deterministic math tools for calculations rather than relying on LLMs to invent numbers.
4. **Transparent Explainability**: "Why do you believe this?" — all findings trace back through explicit claim $\rightarrow$ evidence $\rightarrow$ document source $\rightarrow$ exact page/section mappings.