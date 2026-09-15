# Agentic Multimodal Research Platform

<p align="left">
  <a href="https://github.com/Om-Talaviya"><img src="https://img.shields.io/badge/Architect-Om%20Talaviya-38bdf8?style=flat-square&logo=github&logoColor=white" alt="Author" /></a>
  <img src="https://img.shields.io/badge/Python-3.11+-3776ab?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Framework-FastAPI%20%26%20LangGraph-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Modality-Multimodal%20RAG-7c3aed?style=flat-square" alt="Multimodal" />
  <img src="https://img.shields.io/badge/Status-Phase%2038%20Complete%20(Generation%2012%20Active)-success?style=flat-square" alt="Status" />
  <img src="https://img.shields.io/badge/Tests-399%20Passing-brightgreen?style=flat-square" alt="Tests" />
  <img src="https://img.shields.io/badge/SDKs-Python%20%26%20TypeScript-blueviolet?style=flat-square" alt="SDKs" />
  <img src="https://img.shields.io/badge/Branch-develop%2Fv1.1-blue?style=flat-square" alt="Branch" />
</p>

An enterprise-grade, local-first **AI Research Operating System** that conducts autonomous, verifiable, and evidence-grounded investigations across multiple modalities (text, academic PDFs, DOCX, datasets, images, speech/audio, video, patents, clinical protocols, codebases, and the live web).

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
  • User Context Flow    • Ollama / Gemini / OpenAI       • Knowledge Graph & Memory
═════════════════════════════════════════════════════════════════════════════════
```

---

## What Makes This Platform Different?

| Feature | Generic AI Chatbot / Wrapper | Agentic Multimodal Research Platform |
|---|---|---|
| **Execution Paradigm** | Single-prompt `Question $\rightarrow$ LLM $\rightarrow$ Answer` | Multi-agent DAG `Plan $\rightarrow$ Search $\rightarrow$ Read $\rightarrow$ Critique $\rightarrow$ Synthesize` |
| **Model Coupling** | Locked to a single proprietary API | **Model-Agnostic Routing**: Dynamically routes tasks to optimal fast, vision, or reasoning models with automated failover |
| **Evidence & Provenance** | Unverifiable assertions & frequent hallucinations | **Strict Claim $\rightarrow$ Evidence Mapping**: Every claim links to verified sources, document page numbers, audio/video timestamps, and confidence metrics |
| **Critic & Verification** | No verification loop | Independent `CriticAgent` detects contradictions, audits sufficiency, and triggers iterative research loops |
| **Adversarial Multi-Agent Debates** | Monolithic agreement / echo chamber | `ProposerAgent` vs `OpposerAgent` structured dialectics with Elo rating shifts and `ConsensusArbiter` synthesis |
| **Systematic Literature Reviews** | Surface-level summaries | PRISMA 2020 flow tracking, Cochrane Risk of Bias (RoB 2), and quantitative meta-analysis (Forest plots, Cohen's $d$, Hedges' $g$) |
| **In-Silico Reproducibility** | Untested code snippets | AST-sandboxed computational execution, statistical delta scoring, and deterministic replication verification |
| **Multimodal Presentations & Podcasts** | Static text dumps | Autonomous 16:9 presentation slide decks and multi-speaker podcast audio briefings with conversational banter |
| **Peer Review & Academic Publishing** | Manual formatting | Double-blind referee panels, point-by-point author rebuttals, and camera-ready LaTeX/BibTeX preprint generation |
| **Research Canvas & Ideation** | Rigid linear lists | Infinite 2D interactive spatial canvas, visual DAG layout, and agentic brainstorming nodes |
| **Synthetic Dataset Generation** | Manual prompt labeling | Evol-Instruct evolutionary mutation engine, Alpaca/ShareGPT/DPO/CoT adapters, and active learning curation |
| **Patent Landscape Analysis** | High legal/IP search friction | Autonomous 35 U.S.C. 102/103 prior art claim charts, FTO clearance scoring, and white-space opportunity mapping |
| **Data Ingestion** | Raw text only | Native extraction for multi-page PDFs with tables, DOCX, images, audio speech tracks, and video timelines |
| **Long-Term Memory & Graph** | Session-only context | Persistent cross-session research memory and relational Knowledge Graph with Graph-Augmented RAG (`GraphRAG`) |
| **Multi-Tenancy & Quotas** | Simple API keys or no quotas | Persistent RBAC, transactional row-locking token/cost quotas, and per-user usage attribution |

---

## Current Status & Evolution

The project is currently at **Phase 38 Complete — Generation 12 Active & Fully Delivered** on the stable branch `develop/v1.1` (399/399 unit & integration tests passing).

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
Phase 11: Advanced Research Planning [████████████████████] 100% (Commit: c3b639d)
Phase 12: Advanced Multimodal Intel  [████████████████████] 100% (Commit: f52e694)
Phase 13: Dataset & Data Analysis    [████████████████████] 100% (Commit: 81a5f5d)
Phase 14: Document & Paper Intel     [████████████████████] 100%
Phase 15: Deep Research Engine       [████████████████████] 100%
Phase 16: Research Memory            [████████████████████] 100%
Phase 17: Long-Term Knowledge Graph  [████████████████████] 100%
Phase 18: Projects & Workspaces      [████████████████████] 100%
Phase 19: Team Collaboration         [████████████████████] 100%
Phase 20: Intelligent Model Ecosys   [████████████████████] 100%
Phase 21: Model Evaluation System    [████████████████████] 100%
Phase 22: Agent Evaluation           [████████████████████] 100%
Phase 23: Enterprise Security        [████████████████████] 100%
Phase 24: Production Infrastructure  [████████████████████] 100%
Phase 25: Public API & Dev Platform  [████████████████████] 100%
Phase 26: Research Automation        [████████████████████] 100%
Phase 27: Multi-Agent Debate Engine  [████████████████████] 100%
Phase 28: Systematic Literature Rev  [████████████████████] 100%
Phase 29: In-Silico Reproducibility  [████████████████████] 100%
Phase 30: Multimodal Presentation    [████████████████████] 100%
Phase 31: Peer Review & Publishing   [████████████████████] 100%
Phase 32: Research Canvas Studio     [████████████████████] 100%
Phase 33: Synthetic Dataset Gen      [████████████████████] 100%
Phase 34: Patent Landscape & FTO     [████████████████████] 100%
Phase 35: Scientific Grant Studio    [████████████████████] 100%
Phase 36: Clinical Trials & Repurp   [████████████████████] 100%
Phase 37: Robotic Lab Automation     [████████████████████] 100%
Phase 38: Bio-Molecular 3D Structure [████████████████████] 100%
─────────────────────────────────────────────────────────────────────────────────
ALL 38 PHASES (GENERATIONS 1 - 12) COMPLETED & FULLY ACTIVE (399 TESTS PASSING)
```

---

## 12-Generation Product Architecture (Phases 1 – 38)

- **Generation 1: Intelligent Research Core (Phases 9–11)**: Automated knowledge ingestion, fine-grained evidence citation anchoring, and hierarchical query planning.
- **Generation 2: Multimodal Intelligence (Phases 12–14)**: Speech/video sync, tabular data science profiling, and academic paper hierarchical parsing.
- **Generation 3: Autonomous Research & Memory (Phases 15–17)**: Deep recursive hypothesis loops, cross-session episodic memory, and relational Knowledge Graph with GraphRAG.
- **Generation 4: Enterprise Collaboration (Phases 18–19)**: Workspaces, multi-user project scoping, team invites, and collaborative report annotations.
- **Generation 5: Intelligent Model Ecosystem (Phases 20–22)**: Multi-parameter model Pareto routing, benchmark suites, and agent observability telemetry.
- **Generation 6: Enterprise Security & Dev Platform (Phases 23–25)**: Envelope encryption (AES-256-GCM), tamper-evident Merkle hash audit chains, worker cluster queuing, S3 storage abstraction, and scoped Developer API keys.
- **Generation 7: Research Automation & Synthesis (Phases 26–27)**: Recurring research sweeps, diff scoring, multi-channel alerts, and adversarial Proposer vs Opposer dialectic debate arenas.
- **Generation 8: Systematic Evidence & Publishing (Phases 28–31)**: PRISMA systematic literature reviews, meta-analysis forest plots, sandboxed in-silico code reproducibility, 16:9 presentations, podcast briefings, and double-blind peer review with camera-ready LaTeX preprint publication.
- **Generation 9: Creative Ideation & Instruction Tuning (Phases 32–33)**: 2D infinite collaborative spatial Research Canvas and active learning Evol-Instruct synthetic dataset generation.
- **Generation 10: Legal & Translational Science (Phases 34–35)**: Patent landscape claim charts, FTO clearance, and multi-year NIH/NSF grant proposal synthesis with institutional budgets.
- **Generation 11: Clinical & Experimental Translation (Phases 36–37)**: Clinical trial protocol design, cohort eligibility criteria, drug repurposing target matching, and robotic wet-lab automation protocol compilation (Opentrons Python API v2, PyLabRobot, Autoprotocol).
- **Generation 12: Structural Biology & Molecular Therapeutics (Phase 38)**: AlphaFold3 & ESMFold 3D protein structure prediction, per-residue pLDDT confidence spectrum mapping, catalytic cavity detection, in-silico AutoDock-Vina ligand docking, and thermodynamic $\Delta\Delta G$ mutational stability scanning.
- **Phase 16: Research Memory (COMPLETE)**: Persistent cross-session research memory architecture (`DBResearchMemory`, `MemoryRepository`, `ResearchMemoryManager`), automatic report-to-memory consolidation (findings, methodologies, hypotheses, insights, summaries), semantic & text recall tools (`RecallMemoryTool`, `StoreMemoryTool`), REST APIs (`/api/v1/memory`), and interactive React UI (`ResearchMemoryViewer.tsx` & `MemoryPage.tsx`).
- **Phase 17: Long-Term Knowledge Graph (COMPLETE)**: Entity-relationship graph database models (`DBKnowledgeEntity`, `DBKnowledgeRelation`), `KnowledgeGraphRepository` (subgraph extraction, shortest path BFS), `KnowledgeGraphEngine` (triplet extraction from findings/reports, Graph-Augmented RAG `GraphRAG`), agent tools (`QueryKnowledgeGraphTool`, `ExtractGraphTripletsTool`, `FindRelationPathTool`), REST API (`/api/v1/graph`), and interactive React network visualization studio (`KnowledgeGraphViewer.tsx` & `KnowledgeGraphPage.tsx`).

### Generation 4: Enterprise & Team (100% COMPLETE)
- **Phase 18: Projects & Workspaces (COMPLETE)**: Multi-tenant workspace hierarchies (`DBWorkspace`, `DBWorkspaceMember`, `DBProject`, `WorkspaceRepository`, `ProjectRepository`), RBAC role assignments, REST APIs (`/api/v1/workspaces`, `/api/v1/projects`), and interactive workspace management studio (`WorkspaceSelector.tsx`, `ProjectsPage.tsx`).
- **Phase 19: Team Collaboration (COMPLETE)**: Workspace invitation lifecycle (`DBWorkspaceInvite`), report inline comments & annotations (`DBReportAnnotation`), workspace activity audit trails (`DBWorkspaceActivity`), collaboration repositories, REST APIs (`/api/v1/workspaces/{id}/invites`, `/api/v1/invites/{token}`, `/api/v1/reports/{id}/annotations`), and interactive collaboration modals (`WorkspaceMembersModal.tsx`, `ReportAnnotationsDrawer.tsx`).

### Generation 5: AI Platform Intelligence (100% COMPLETE)
- **Phase 20: Intelligent Model Ecosystem (COMPLETE)**: Multi-parameter optimization profiles (`SpeedMaximized`, `CostMinimized`, `QualityMaximized`, `BalancedAdaptive`), latency/cost/quality threshold trade-off modeling, Pareto frontier selection, and `/api/v1/models/optimize` REST endpoints.
- **Phase 21: Model Evaluation System (COMPLETE)**: Multi-dimensional automated benchmarking engine (`BenchmarkDataset`, `EvaluationMetricsEngine`, `ModelEvaluator`), ground-truth factual/reasoning/retrieval evaluation, database persistence (`DBModelEvaluation`, `DBModelBenchmarkResult`), REST APIs (`/api/v1/models/evaluate`, `/api/v1/models/evaluations`, `/api/v1/models/leaderboard`), and interactive Model Benchmarks leaderboard studio (`ModelEvaluationPage.tsx`).
- **Phase 22: Agent Evaluation & Observability (COMPLETE)**: Multi-metric autonomous agent evaluation engine (`AgentEvaluator`, `AgentEvaluationScorecard`, `AgentStepTelemetry`), plan precision scoring, tool invocation accuracy, evidence grounding coverage, sentence-level hallucination rate detection, database persistence (`DBAgentEvaluation`, `DBAgentStepMetric`, `AgentEvaluationRepository`), REST APIs (`/api/v1/agents/evaluate`, `/api/v1/agents/evaluations`, `/api/v1/agents/metrics/summary`), and interactive Agent Observability Studio (`AgentEvaluationPage.tsx`).

### Generation 6: Production Product (100% COMPLETE)
- **Phase 23: Enterprise Security (COMPLETE)**: Two-tier KMS envelope encryption (AES-256-GCM DEK/KEK), tamper-evident SHA-256 cryptographic audit hash chaining (`AuditHashChainer`), workspace security & data retention policies (`DBSecurityPolicy`), GDPR Article 17 cascade purge (`execute_gdpr_data_purge`), SOC 2 compliance scorecard APIs, and `EnterpriseSecurityPage.tsx` React studio.
- **Phase 24: Production Infrastructure (COMPLETE)**: Distributed asynchronous priority task queues (`AsyncTaskQueue`), worker cluster node telemetry (`WorkerNode`, `DBWorkerNode`), S3/MinIO/Local blob vault (`ObjectStorageClient`, `DBStorageObject`), presigned URL generation, and `ProductionInfrastructurePage.tsx` React studio.
- **Phase 25: Public API & Developer Platform (COMPLETE)**: Public REST gateway (`/api/v1/developer/*`), cryptographically secure SHA-256 hashed API keys (`DBApiKey`, `ApiKeyRepository`), granular permission scopes (`research:read/write`, `documents:read/write`, `memory:read`, `graph:read`), sliding window rate limiting tiers (Free, Pro, Enterprise), interactive API Playground with live cURL / Python / TypeScript SDK snippets, and `DeveloperPlatformPage.tsx` React studio.
- **Phase 26: Research Automation (COMPLETE)**: Autonomous recurring research sweeps, cron and interval scheduling (`compute_next_run`), semantic claim diff engine, novelty scoring ($\text{novelty} \in [0.0, 1.0]$), threshold-triggered multi-channel alerts (in-app, email, webhooks), database models (`DBScheduledResearch`, `DBResearchSweepResult`, `DBAutomationAlert`), `AutomationRepository`, `/api/v1/automation/*` REST endpoints, and `ResearchAutomationPage.tsx` React studio.

### Generation 7: Scientific & Meta-Intelligence (100% COMPLETE)
- **Phase 27: Adversarial Multi-Agent Debate & Consensus Engine (COMPLETE)**: Multi-agent dialectical debate studio (`ProposerAgent` vs `OpposerAgent`), dynamic Elo rating shift tracking ($\Delta R = K \times (S - E)$), impartial arbitration and round critique (`ConsensusArbiter`), dialectical consensus synthesis (accepted claims, refuted claims, mutual concessions, residual uncertainties, factual confidence), database models (`DBAgentDebate`, `DBDebateRound`, `DBDebateConsensus`), `DebateRepository`, `/api/v1/debates/*` REST API, and `DebateArenaPage.tsx` React studio.
- **Phase 28: Systematic Literature Review & Meta-Analysis Engine (COMPLETE)**: PRISMA 2020 four-stage study flow tracking, Cochrane Risk of Bias 2.0 (RoB 2) multi-domain quality scoring, quantitative meta-analysis statistical pooling (Forest plot generation, Cohen's $d$, Hedges' $g$, inverse-variance weighting, Cochran's $Q$, Higgins $I^2$ heterogeneity index), database models (`DBLiteratureReview`, `DBSLRCriterion`, `DBSLRStudyCandidate`, `DBMetaAnalysisReport`, `DBRiskOfBiasAssessment`), `LiteratureRepository`, `/api/v1/literature/*` REST API, and `LiteratureReviewPage.tsx` React studio.
- **Phase 29: In-Silico Experimentation & Computational Reproducibility Engine (COMPLETE)**: AST-sandboxed computational code execution, empirical claim verification traces, numerical and statistical delta scoring ($\Delta \le \epsilon$), replication pass/fail status determination, database models (`DBExperimentProtocol`, `DBReproducibilityRun`, `DBClaimVerificationTrace`), `ReproducibilityRepository`, `ReproducibilityEngine`, `/api/v1/reproducibility/*` REST API, and `ReproducibilityPage.tsx` React studio.
- **Phase 30: Multimodal Scientific Presentation & Executive Podcasting Generator (COMPLETE)**: Autonomous structured presentation slide deck generator (16:9 slides, Markdown speaker notes, visual card grids, key takeaways), multi-speaker executive podcast audio script synthesizer (Host & Analyst roles, conversational dialogue banter, tone markers), database models (`DBSynthesisPresentation`, `DBPresentationSlide`, `DBPodcastBriefing`), `PresentationRepository`, `PresentationGenerator`, `PodcastBriefingSynthesizer`, `/api/v1/presentations/*` REST API, and `PresentationStudioPage.tsx` React studio.

### Generation 8: Autonomous Meta-Science & Publishing Ecosystem (100% COMPLETE)
- **Phase 31: Autonomous Scientific Peer Review & Journal Publishing Pipeline (COMPLETE)**: Multi-agent double-blind academic peer review simulator (Methodology, Statistical, and Domain Specialist reviewer personas), weighted scorecards, author rebuttals with point-by-point response tracking, camera-ready academic publishing generator (Nature, IEEE, ACM, arXiv LaTeX source, BibTeX entries, and DOI minting), database models (`DBPeerReviewManuscript`, `DBPeerReviewReport`, `DBManuscriptRevision`), `PeerReviewRepository`, `PeerReviewEngine`, `PublicationFormatter`, `AuthorRebuttalGenerator`, `/api/v1/publishing/*` REST API, and `PeerReviewPage.tsx` React studio.
- **Phase 32: Real-Time Collaborative Research Canvas & Visual Ideation Studio (COMPLETE)**: Infinite 2D spatial canvas, node-link visual DAG representations (`DBCanvasBoard`, `DBCanvasNode`, `DBCanvasEdge`), automated DAG layout from research dossiers, real-time agentic brainstorming nodes, clustering by entity type, `CanvasRepository`, `CanvasIdeationEngine`, `/api/v1/canvas/*` REST API, and `ResearchCanvasPage.tsx` React studio.
- **Phase 33: Synthetic Instruction Dataset Generation & Active Learning Engine (COMPLETE)**: Evolutionary prompt mutator (`InstructionDatasetSynthesizer` with `in_depth_expansion`, `in_breadth_variation`, `constraint_hardening`, `adversarial_redteaming`, `cot_decomposition`), format adapters (Alpaca SFT, ShareGPT Multi-Turn, DPO Preference Pairs, Chain-of-Thought), deterministic quality/toxicity/hallucination/dedup scoring, active learning human-in-the-loop curation studio, database models (`DBSyntheticDataset`, `DBInstructionSample`, `DBAlignmentExport`), `DatasetSynthesisRepository`, `/api/v1/datasets/*` REST API, and `DatasetSynthesisPage.tsx` React studio.
- **Phase 34: Autonomous Patent Landscape Analysis & Prior Art Search Engine (COMPLETE)**: Decomposition of patent claims into atomic preambles, transitional phrases, and limitations, 35 U.S.C. 102 (Anticipation) and 103 (Non-Obviousness) prior art claim charts, Freedom-to-Operate (FTO) clearance percentage scoring, white-space patentability opportunity discovery, automated design-around mitigations, database models (`DBPatentCorpus`, `DBPatentDocument`, `DBPatentClaim`, `DBPriorArtEvaluation`, `DBFreedomToOperateReport`), `PatentRepository`, `PatentPriorArtEngine`, `/api/v1/patents/*` REST API, and `PatentLandscapePage.tsx` React studio.

### Generation 9: Autonomous Scientific Grant & Research Funding Studio (100% COMPLETE)
- **Phase 35: Autonomous Scientific Grant & Research Funding Proposal Synthesizer (COMPLETE)**: Specific Aims and narrative module generator, institutional multi-year budget calculator (`InstitutionalBudgetCalculator` with MTDC, fringe benefits, and 52% F&A indirect cost recovery), mock NIH study section peer review panel simulator with 1.0-9.0 criterion ratings, compilable LaTeX grant proposal generator, database models (`DBGrantProposal`, `DBGrantSpecificAim`, `DBGrantBudgetItem`, `DBGrantReviewScorecard`), `GrantProposalRepository`, `GrantProposalSynthesizer`, `/api/v1/grants/*` REST API, and `GrantProposalStudioPage.tsx` React studio.

### Generation 10: Clinical Intelligence & Developer Ecosystem (100% COMPLETE)
- **Phase 36: Autonomous Clinical Trial Protocol & Drug Repurposing Engine (COMPLETE)**: Autonomous PICO cohort eligibility criteria synthesizer, molecular target-affinity repurposing screen, adverse risk quantification, and eCTD FDA IND / EMA CTD electronic regulatory compliance dossier generator, database models (`DBClinicalProtocol`, `DBCohortCriterion`, `DBDrugCandidate`, `DBRegulatoryPackage`), `ClinicalRepository`, `ClinicalTrialEngine`, `/api/v1/clinical/*` REST API, and `ClinicalTrialsPage.tsx` React studio.
- **Official Developer Platform SDKs (COMPLETE)**: Async Python developer SDK (`packages/sdk-python/ai_research_os`) and isomorphic TypeScript Client SDK (`apps/web/src/sdk/client.ts`) with typed models, polling helpers, rate limit handlers, and connection pooling.
- **Production Demo Data Seeder (COMPLETE)**: Multi-modal, cross-studio sample dataset seeder (`scripts/seed_demo_data.py`) spanning all 36 platform studios with the flagship project *"Targeted CRISPR-Cas9 Epigenetic Editing via Lipid Nanoparticle Delivery for Monogenic Hepatopathies"*.

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