# System Architecture Documentation: ARCHITECTURE.md

## High-Level System Architecture

The **Agentic Multimodal Research Platform** is engineered as a modular, local-first **AI Research Operating System**. It moves beyond standard single-turn chatbots by employing a coordinated, Directed Acyclic Graph (DAG) based agentic workflow that plans, investigates, retrieves, reasons, critiques, synthesizes, and reports on complex multi-domain questions.

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
                                         │ HTTPS / WSS
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

## 1. Core Architectural Pillars

### 1.1 Dependency Inversion & Provider Agnosticism
High-level agent logic depends strictly on abstract protocols (`packages/ai`):
- `LLMProvider` $\rightarrow$ `OllamaProvider`, `GeminiProvider`, `OpenAICompatibleProvider`.
- `VisionProvider` $\rightarrow$ Multimodal model endpoints.
- `EmbeddingProvider` $\rightarrow$ Vector embedders (`nomic-embed-text`, etc.).
- `VectorStore` $\rightarrow$ `ChromaStore`, `InMemoryStore`.

### 1.2 Multi-Tier AI Routing & Gateway Hierarchy (Phase 8A & 8B)
```
  Agent Request (AgentContext + TaskType)
                     │
                     ▼
             ┌──────────────┐
             │ ModelGateway │
             └───────┬──────┘
                     │
                     ▼
             ┌──────────────┐
             │ ModelRouter  │
             └───────┬──────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
┌─────────────────┐     ┌──────────────────┐
│  ModelRegistry  │     │ ProviderRegistry │
│ (Capabilities)  │     │ (Health & Auth)  │
└─────────────────┘     └──────────────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
        ┌─────────────────────────┐
        │ Quota Verification Lock │
        │ (SELECT ... FOR UPDATE) │
        └────────────┬────────────┘
                     │
                     ▼
        ┌─────────────────────────┐
        │ Concrete Provider Call  │
        │ (Ollama, Gemini, OpenAI)│
        └────────────┬────────────┘
                     │
                     ▼
        ┌─────────────────────────┐
        │  Usage Telemetry Log    │
        │  (UsageRecord in DB)    │
        └─────────────────────────┘
```

1. **`ModelRegistry`**: Catalog of registered models, capabilities (`STREAMING_RESPONSE`, `VISION_ANALYSIS`, `FACTUAL_EXTRACTION`, `SYNTHESIS`), context sizes, and priority scores.
2. **`ProviderRegistry`**: Manages live provider instances, connection pooling, and health status.
3. **`ModelRouter`**: Dynamically maps task requirements and constraints to candidate models.
4. **`ModelGateway`**: High-level execution entry point that handles model selection, fallback execution on rate limits/errors, quota verification, and telemetry logging.
5. **Usage & Quotas**: Persistent `UsageRecord` and `UserQuota` models with transactional row locking to eliminate race conditions under concurrent worker executions.

---

## 2. Research Engine & Agentic Orchestration

### 2.1 Dynamic DAG Task Execution
The research process is modeled as an executable Directed Acyclic Graph:
```mermaid
graph TD
    A[User Research Question] --> B[PlannerAgent]
    B --> C[Generate Task DAG]
    C --> D1[Task 1: Web Search]
    C --> D2[Task 2: Ingest Document Context]
    D1 --> E[CriticAgent: Verify Evidence]
    D2 --> E
    E --> F{Evidence Sufficient?}
    F -->|No: Gaps Found| G[Schedule Iterative Subtask]
    G --> D1
    F -->|Yes| H[ReportAgent: Synthesis & Provenance]
    H --> I[Final Research Report]
```

### 2.2 Agent Roles & Specialization
- **`PlannerAgent`**: Deconstructs broad questions into structured subtasks with explicit dependencies (`depends_on`).
- **`WebResearchAgent`**: Executes web search queries and retrieves sanitized web pages using `SSRF-safe` network adapters.
- **`DocumentAnalysisAgent`**: Retrieves and extracts relevant passages from local uploaded PDFs, DOCX, and images.
- **`CriticAgent`**: Audits factual claims, calculates confidence metrics, detects source contradictions, and flags unverified assertions.
- **`ReportAgent`**: Compiles verified evidence into an executive summary, findings, methodology, conclusions, and citation map.

---

## 3. Multimodal Ingestion & Hybrid RAG Architecture

```mermaid
flowchart LR
    Doc[User Documents: PDF, DOCX, Img] --> Parse[Parser Layer]
    Parse --> Chunk[Semantic Chunker]
    Chunk --> Embed[Vector Embedder]
    Chunk --> Lexical[BM25 Tokenizer]
    Embed --> Chroma[(ChromaDB)]
    Lexical --> BM25Index[(BM25 Sparse Store)]
    
    Query[Agent Search Query] --> DenseSearch[Dense Vector Query]
    Query --> SparseSearch[BM25 Lexical Query]
    DenseSearch --> RRF[Reciprocal Rank Fusion RRF]
    SparseSearch --> RRF
    RRF --> Context[Ranked Grounded Context]
```

---

## 4. User Context Flow & Persistence

Authenticated requests flow through the entire system with complete user attribution:
```
  FastAPI JWT Authentication (/api/v1/auth)
                     │
                     ▼ (Extract authenticated user_id)
        Endpoint: POST /api/v1/research
                     │
                     ▼ (Pass user_id into pipeline)
             ResearchPipeline
                     │
                     ▼ (Initialize orchestrator with context)
             AgentOrchestrator
                     │
                     ▼ (Propagate into AgentContext)
               AgentContext
                     │
                     ▼ (Invoke LLM with user context)
               ModelGateway
                     │
                     ▼ (Record tokens & cost)
             UsageRepository
                     │
                     ▼
          Database (UsageRecord.user_id)
```

---

## 5. The 6-Generation Long-Term Architecture (Phases 9 – 26)

### Generation 1: Intelligent Research Core (Phases 9 – 11)
- **Phase 9 (Knowledge Automation - COMPLETE)**: Automated document ingestion daemon and planner-integrated retrieval.
- **Phase 10 (Evidence & Citation Intelligence - COMPLETE)**: Fine-grained claim-to-source anchoring with page/paragraph coordinates and pairwise contradiction detection.
- **Phase 11 (Advanced Research Planning - COMPLETE)**: Hierarchical planning engine with `QueryTreeNode` recursive subquestion decomposition and closed-loop replanning.

### Generation 2: Multimodal Intelligence (Phases 12 – 14) (COMPLETE)
- **Phase 12 (Advanced Multimodal Research - COMPLETE)**: Unified multi-modal context assembler for 50+ page PDFs, images, charts (`ChartRef`), and audio/video timestamp transcripts (`[MM:SS - MM:SS]`).
- **Phase 13 (Dataset & Data Analysis Intelligence - COMPLETE)**: Tabular data analysis (CSV, TSV, Excel, JSON) using deterministic Python calculation tools (`DataAnalysisTool`, `DeterministicMathTool`, `TabularParser`).
- **Phase 14 (Document & Paper Intelligence - COMPLETE)**: Academic research paper parser (`AcademicPaperParser`), section tree hierarchies (`PaperSection`), BibTeX citation matching, and cross-paper comparative matrices (`PaperAnalysisTool`, `MethodologyComparisonTool`).

### Generation 3: Autonomous Research (Phases 15 – 17) (COMPLETE)
- **Phase 15 (Deep Research Engine - COMPLETE)**: Autonomous recursive multi-round research loops (`DeepResearchEngine`), recursive gap & hypothesis formulation with `CriticAgent`, adaptive DAG expansion with `PlannerAgent.replan()`, strict convergence guardrails ($\tau \ge 0.85$, max iterations, $\Delta \tau < 0.02$), WebSocket iteration telemetry, and `DeepResearchTracker.tsx` timeline studio.
- **Phase 16 (Research Memory - COMPLETE)**: Cross-session persistent research memory (`DBResearchMemory`, `MemoryRepository`, `ResearchMemoryManager`), semantic conceptual indexing, agent memory tools (`RecallMemoryTool`, `StoreMemoryTool`), REST API (`/api/v1/memory`), and interactive `ResearchMemoryViewer` UI.
- **Phase 17 (Long-Term Knowledge Graph - COMPLETE)**: Relational entity-relationship adjacency persistence (`DBKnowledgeEntity`, `DBKnowledgeRelation`, `KnowledgeGraphRepository`), `KnowledgeGraphEngine` (triplet extraction from findings/reports, Graph-Augmented RAG `GraphRAG`), agent tools (`QueryKnowledgeGraphTool`, `ExtractGraphTripletsTool`, `FindRelationPathTool`), REST API (`/api/v1/graph`), and interactive React network visualization studio (`KnowledgeGraphViewer.tsx` & `KnowledgeGraphPage.tsx`).

### Generation 4: Collaboration Platform (Phases 18 – 19) (COMPLETE)
- **Phase 18 (Projects & Workspaces - COMPLETE)**: Hierarchical tenant isolation (`User $\rightarrow$ Workspace $\rightarrow$ Projects $\rightarrow$ Knowledge & Research`), `DBWorkspace`, `DBWorkspaceMember`, `DBProject`, `WorkspaceRepository`, `ProjectRepository`, REST APIs (`/workspaces`, `/projects`), `WorkspaceSelector` and `ProjectsPage` UI.
- **Phase 19 (Team Collaboration - COMPLETE)**: Granular workspace RBAC (`owner`, `admin`, `researcher`, `analyst`, `reviewer`, `viewer`), cryptographic email invitation lifecycle (`DBWorkspaceInvite`, `WorkspaceInviteRepository`), threaded report annotations with quotes and 1-click resolution (`DBReportAnnotation`, `ReportAnnotationsDrawer.tsx`), and collaborative audit activity logs (`DBWorkspaceActivity`).

### Generation 5: AI Platform Intelligence (Phases 20 – 22) (COMPLETE)
- **Phase 20 (Intelligent Model Ecosystem - COMPLETE)**: Multi-parameter utility routing optimization engine (`ModelEcosystemOptimizer`), Pareto-frontier non-dominated sorting across Quality, Speed, Cost, and Locality, preset optimization profiles (Balanced, Cost, Speed, Quality), and `/models/profiles` + `/models/optimize` REST endpoints (**ADR 020**).
- **Phase 21 (Model Evaluation System - COMPLETE)**: Ground-truth benchmark harness (`BenchmarkDataset`, `DEFAULT_RESEARCH_BENCHMARK`), automated multi-dimensional scoring (`EvaluationMetricsEngine` - factuality, reasoning, faithfulness, citations, latency, cost), persistence (`DBModelEvaluation`, `ModelEvaluationRepository`), REST APIs (`/models/evaluate`, `/models/evaluations`, `/models/leaderboard`), and competitive Leaderboard studio (`ModelEvaluationPage.tsx`) (**ADR 021**).
- **Phase 22 (Agent Evaluation - COMPLETE)**: Autonomous multi-metric agent evaluation engine (`AgentEvaluator`, `AgentEvaluationScorecard`, `AgentStepTelemetry`), plan precision scoring, tool invocation accuracy, evidence grounding coverage, sentence-level hallucination rate detection, database persistence (`DBAgentEvaluation`, `DBAgentStepMetric`, `AgentEvaluationRepository`), REST APIs (`/api/v1/agents/evaluate`, `/api/v1/agents/evaluations`, `/api/v1/agents/metrics/summary`), and interactive Agent Observability Studio (`AgentEvaluationPage.tsx`) (**ADR 022**).

### Generation 6: Production Product (Phases 23 – 26) (ACTIVE GENERATION - Phase 25 Next)
- **Phase 23 (Enterprise Security - COMPLETE)**: KMS two-tier envelope encryption (AES-256-GCM DEK/KEK with PBKDF2 salt derivation), tamper-evident SHA-256 cryptographic audit hash chaining (`AuditHashChainer`), workspace security & data retention policies (`DBSecurityPolicy`), automated GDPR Article 17 cascade purge (`execute_gdpr_data_purge`), SOC 2 compliance scorecard APIs, and `EnterpriseSecurityPage.tsx` React studio (**ADR 023**).
- **Phase 24 (Production Scale Infrastructure - COMPLETE)**: In-memory and distributed asynchronous task queues (`AsyncTaskQueue` priority heap with `CRITICAL`, `HIGH`, `DEFAULT`, `LOW` scheduling), worker node cluster tracking (`WorkerNode`, `DBWorkerNode`), S3/MinIO/Local unified blob storage vault (`ObjectStorageClient`, `DBStorageObject`), `InfrastructureRepository`, REST APIs (`/api/v1/system`), and `ProductionInfrastructurePage.tsx` React cluster topology studio (**ADR 024**).
- **Phase 25 (Public API & Developer Platform - 🟡 IMMEDIATE NEXT MILESTONE)**: Public OpenAPI 3.1 gateway, developer API key provisioning with SHA-256 secret hashing, granular permission scopes, per-tier rate limiting, and official Python/TypeScript SDK implementations.
- **Phase 26 (Research Automation)**: Cron-based research workers with automated web/academic change detection.

---

## 6. Architectural Anti-Patterns ("What We Should NOT Do")

To prevent engineering decay and maintain structural velocity:
1. **No Premature Complexity**: We will not introduce distributed message queues (Kafka), microservices, OAuth federations, or additional vector databases before the core agentic research loops are tightly integrated and proven.
2. **No Generative Arithmetic**: LLMs must never perform arithmetic or statistical computations directly; all calculations are executed via deterministic tools.
3. **Core Philosophy**: **Make the research engine excellent first $\rightarrow$ make knowledge deeply integrated $\rightarrow$ make evidence trustworthy $\rightarrow$ make multimodal analysis powerful $\rightarrow$ make it collaborative $\rightarrow$ make it production-grade.**