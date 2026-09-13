# Architecture Decision Records (ADR): decisions.md

This document records the key architectural, engineering, and product design decisions made throughout the lifecycle of the **Agentic Multimodal Research Platform (AI Research OS)**.

---

## ADR 001: Provider-Agnostic AI Architecture
- **Status**: Accepted & Implemented (Phase 1 & Phase 8A)
- **Context**: The platform requires support for local inference (Ollama) for data privacy as well as cloud inference (Google Gemini, OpenAI-compatible APIs) for intensive reasoning tasks. Directly coupling agent code to vendor SDKs creates vendor lock-in.
- **Decision**: Define protocol-based abstractions (`LLMProvider`, `VisionProvider`, `EmbeddingProvider`, `RerankerProvider`) in `packages/ai` and decouple all agent implementations from concrete SDKs.
- **Consequences**:
  - Positive: Seamless swapping and mocking of model backends without modifying agent business logic.
  - Positive: High testability with zero network flakiness in automated unit and integration test suites.

---

## ADR 002: ModelGateway $\rightarrow$ ModelRouter $\rightarrow$ ModelRegistry Subsystem (Phase 8A)
- **Status**: Accepted & Implemented (September 2026 - Commit: `88ac57d`)
- **Context**: As multiple models and providers were introduced, agents needed dynamic selection based on required capabilities (e.g., vision, streaming, structured JSON output) rather than hardcoded model strings, with automatic fallback handling.
- **Decision**: Implement a four-tier architecture:
  1. `ModelRegistry`: Maintains catalog, priority scores, and task suitability mappings.
  2. `ProviderRegistry`: Manages concrete provider instances and provider health checks.
  3. `ModelRouter`: Evaluates matching candidate models based on task type and capabilities.
  4. `ModelGateway`: High-level entry point orchestrating routing, automatic fallback failover, latency tracking, and telemetry attachment.
- **Consequences**:
  - Positive: Transparent failover if a primary provider experiences transient rate limits (HTTP 429) or outages.
  - Positive: Single point of telemetry collection for token counting and latency observability.

---

## ADR 003: Migration to Official Google Gemini Provider & Removal of Web2API
- **Status**: Accepted & Implemented (Phase 7.3)
- **Context**: Early experimental prototyping used an unofficial `GeminiWeb2API` browser-scraping adapter. This was fragile, violated API terms, and lacked enterprise stability.
- **Decision**: Completely delete `gemini_web2api.py` and replace it with `ai.providers.gemini.GeminiProvider` using the official `google-genai` / REST API.
- **Consequences**:
  - Positive: Enterprise reliability, low latency, official streaming, and clean authentication via `GEMINI_API_KEY`.
  - Positive: Eliminated unstable browser automation dependencies.

---

## ADR 004: Persistent PostgreSQL User Authentication & Alembic Migrations
- **Status**: Accepted & Implemented (Phase 7.2)
- **Context**: Initial Phase 6 implementations utilized an in-memory user registry for prototype testing. Production deployments require persistent user credentials, auditability, and schema migration tracking.
- **Decision**: Introduce a dedicated `users` table in PostgreSQL (with SQLite compatibility), managed via Alembic (`001_create_users_table.py`), using PBKDF2-HMAC-SHA256 password hashing and JWT access/refresh token pairs.
- **Consequences**:
  - Positive: Production-ready user persistence, audit logs, and smooth database evolution via Alembic.

---

## ADR 005: Bi-directional WebSocket Streaming with Snapshot Hydration
- **Status**: Accepted & Implemented (Phase 2 & Phase 7.1)
- **Context**: Polling REST endpoints for long-running research jobs causes excessive network traffic and delayed UI state updates.
- **Decision**: Implement a dedicated WebSocket endpoint (`/api/v1/research/{job_id}/ws`). On connection, the server immediately delivers a complete `snapshot` of the job, task DAG, sources, evidence, and report, followed by real-time domain events emitted from `ResearchEventBus`.
- **Consequences**:
  - Positive: Sub-second UI reactivity and zero missed state transitions during rapid task executions.

---

## ADR 006: Persistent Usage Records & Quota Enforcement with Transactional Row Locking (Phase 8B)
- **Status**: Accepted & Implemented (September 2026 - Commit: `a603114`)
- **Context**: Multi-tenant deployments need strict token and cost quotas with accurate user usage tracking. Concurrent agent coroutines could perform stale quota checks and cause oversubscription.
- **Decision**:
  1. Introduce `UserQuota` and `UsageRecord` database models.
  2. Implement transactional row-level locking (`SELECT ... FOR UPDATE`) during quota checks.
  3. Propagate authenticated `user_id` down into `AgentContext` and `ModelGateway`.
  4. Implement quota-aware model fallback (routing to zero-cost Ollama models if cloud quotas are exhausted).
- **Consequences**:
  - Positive: Zero quota oversubscription verified under 10 concurrent worker load testing.
  - Positive: Granular per-inference cost and token observability.

---

## ADR 007: Deterministic Tools for Numerical Calculations vs LLM Guessing
- **Status**: Accepted & Implemented
- **Context**: LLMs frequently hallucinate or generate subtle errors when performing arithmetic, statistical calculations, and table aggregations.
- **Decision**: All quantitative data analysis (means, correlations, regressions, percentages) must be computed using deterministic Python calculation tools and passed as structured evidence to the LLM, rather than asking the LLM to calculate numbers directly in prompt text.
- **Consequences**:
  - Positive: 100% mathematical precision and auditability in synthesized research reports.

---

## ADR 008: Phased 6-Generation Evolutionary Roadmap over Premature Infrastructure Bloat
- **Status**: Accepted
- **Context**: There is a common temptation to add complex distributed infrastructure (Kafka, Kubernetes distributed workers, OAuth microservices, redundant vector databases) before the core research experience is solid.
- **Decision**: Formally adopt the 6-generation evolutionary roadmap (Phases 9 – 26): **Make the research engine excellent first $\rightarrow$ make knowledge deeply integrated $\rightarrow$ make evidence trustworthy $\rightarrow$ make multimodal analysis powerful $\rightarrow$ make it collaborative $\rightarrow$ make it production-grade.**
- **Consequences**:
-   Positive: Protects engineering velocity and ensures every added subsystem delivers immediate user value.

---

## ADR 009: Zero-Touch Dual-Indexing Knowledge Automation (Phase 9)
- **Status**: Accepted & Implemented (September 2026)
- **Context**: Ingested documents were previously only parsed on-demand or required manual indexing steps, creating latency and preventing the planner from anticipating available internal context.
- **Decision**: Introduce immediate background dual-indexing upon upload (`VectorStore` dense embeddings + `BM25Index` sparse lexical tokens), document processing status lifecycle (`pending` $\rightarrow$ `processing` $\rightarrow$ `ready` / `failed`), and planner integration inspecting local knowledge before DAG task compilation.
- **Consequences**:
-   Positive: Instantaneous hybrid retrieval capability across all uploaded documents.
-   Positive: Planner agent creates grounded research plans prioritizing existing internal knowledge before dispatching web searches.

---

## ADR 010: Fine-Grained Citation Coordinates and Contradiction Detection Taxonomy (Phase 10)
- **Status**: Accepted & Implemented (September 2026)
- **Context**: Enterprise research requires verifiable provenance down to exact document coordinates (page, paragraph, table row/col) and automated detection of conflicting findings across distinct sources.
- **Decision**:
  1. Define `CitationCoordinates`, `Citation`, and `Contradiction` domain and database models.
  2. Implement a pairwise contradiction detection engine in `CriticAgent` categorizing conflicts into `direct_conflict`, `numerical_discrepancy`, and `methodological_divergence`.
  3. Synthesize citation-grounded reports in `ReportAgent` with a dedicated contradictions matrix and overall quantitative `confidence_score`.
- **Consequences**:
  - Positive: 100% auditability with interactive claim-to-coordinate explainability.
  - Positive: Explicit identification and taxonomy for all conflicting evidence across sources.

---

## ADR 011: Hierarchical Query Trees & Closed-Loop Adaptive Replanning (Phase 11)
- **Status**: Accepted & Implemented (September 2026)
- **Context**: Complex multi-domain research inquiries cannot be effectively executed as flat lists of independent tasks without structured sub-question hierarchies and adaptive feedback when evidence is missing or contradictory.
- **Decision**:
  1. Implement `QueryTreeNode` recursive subquestion decomposition with quantitative `ambiguity_score` evaluation and `InferredScope` resolution in `PlannerAgent`.
  2. Implement dynamic agent role assignment matching subquestions to specialized agent capabilities.
  3. Implement closed-loop adaptive replanning (`PlannerAgent.replan()`) triggering dynamic task additions (`task_spawned` and `dag_replanned` events) when `CriticAgent` flags evidentiary gaps.
- **Consequences**:
  - Positive: Transparent multi-tier strategic decomposition visible in real-time UI.
  - Positive: Self-healing research execution DAG resolving knowledge blindspots autonomously.

---

## ADR 012: Unified Multimodal Evidence & Timestamp-Bounded Chunking (Phase 12)
- **Status**: Accepted & Implemented (September 2026)
- **Context**: Enterprise multimodal research must digest audio speech recordings, video demonstrations, and scientific charts alongside text, requiring exact time-bounding (`[MM:SS - MM:SS]`), speaker attribution, and structured chart data series extraction.
- **Decision**:
  1. Extend `CitationCoordinates` with `timestamp_start`, `timestamp_end`, `media_type`, `speaker`, and `chart_data`.
  2. Implement `AudioParser` for speech audio and `VideoParser` for synchronized multimodal video timelines.
  3. Implement `ChartRef` structured extraction in `ImageParser` to preserve numerical JSON data series and Markdown tables.
  4. Enhance `SemanticChunker` to generate timestamp-bounded and chart-specific chunks for hybrid RAG dual-indexing.
- **Consequences**:
  - Positive: True cross-modal factual grounding with verifiable timestamp and coordinate provenance.
  - Positive: Deterministic reasoning over extracted scientific chart data series.

---

## ADR 013: Deterministic Data Analysis & Statistical Profiling Engine (Phase 13)
- **Status**: Accepted & Implemented (September 2026)
- **Context**: LLMs exhibit severe arithmetic hallucination and unreliability when asked to perform statistical calculations, aggregations, correlation coefficients, or regression analyses over raw datasets.
- **Decision**:
  1. Implement `TabularParser` for CSV, TSV, Excel, and JSON files to perform automated delimiter sniffing, schema type inference, and statistical column distribution profiling upon ingestion.
  2. Create `DataAnalysisTool` implementing Python-native deterministic calculation operations (`describe`, `aggregate`, `correlation`, `linear_regression`, `filter`).
  3. Create `DeterministicMathTool` evaluating mathematical expressions strictly via safe Python Abstract Syntax Tree (AST) parsing, barring any arbitrary code execution or network/filesystem side-effects.
  4. Equip `DocumentAnalysisAgent` with these deterministic tools, strictly prohibiting raw model calculation estimates (reinforcing **ADR 007**).
  5. Provide `DatasetViewer.tsx` for visual and tabbed inspection of dataset summaries, column metrics, and raw sample records in the React UI.
- **Consequences**:
  - Positive: 100% mathematically exact statistical and regression results with zero LLM arithmetic hallucination.
  - Positive: Safe AST execution without risk of remote code execution or injection vulnerabilities.

---

## ADR 014: Academic Paper Structure Parsing & Cross-Preprint Methodology Intelligence (Phase 14)
- **Status**: Accepted & Implemented (September 2026)
- **Context**: Academic research manuscripts, preprints (arXiv/bioRxiv), and technical reports require deep structural parsing (Abstract, Methods, Results, Limitations, References) rather than naive flat text splitting, and researchers need automated comparative matrices across multiple papers.
- **Decision**:
  1. Implement `PaperSection`, `BibEntry`, and `PaperStructure` models capturing hierarchical section trees (H1/H2/H3), metadata (authors, affiliations, abstract), and bibliographic citations.
  2. Implement `AcademicPaperParser` with heuristic section classification and inline reference anchor extraction (`[1]`, `(Author et al., 2024)`).
  3. Enhance `SemanticChunker` with academic section-aware boundary chunking, preserving section titles and types for targeted hybrid RAG.
  4. Implement `PaperAnalysisTool` and `MethodologyComparisonTool` to extract core research dimensions and generate multi-paper comparative matrices.
  5. Provide `PaperViewer.tsx` (interactive section tree navigation, citation popovers) and `ComparisonMatrix.tsx` (cross-paper methodology diffs) in the React frontend.
- **Consequences**:
  - Positive: High-fidelity academic document navigation and grounded section-level hybrid retrieval.
  - Positive: Automated multi-paper methodology comparison matrices accelerating literature synthesis.

---

## ADR 015: Autonomous Deep Research Engine & Multi-Round Hypothesis Loop Architecture (Phase 15)
- **Status**: Accepted & Implemented (September 2026)
- **Context**: High-stakes scientific and market research cannot conclude after a single linear execution pass. When initial evidence reveals critical gaps, contradictory claims, or low confidence scores ($\tau < 0.85$), the system must autonomously formulate follow-up hypotheses, dynamically schedule targeted investigation subtasks, and iterate until strict convergence criteria are met.
- **Decision**:
  1. Implement `DeepResearchEngine` in `packages/research/src/research/deep_research.py` to orchestrate recursive multi-round feedback loops between `CriticAgent`, `PlannerAgent`, and specialized execution agents.
  2. Structure `DeepResearchConfig` and `ResearchIteration` data contracts in `packages/research/src/research/models.py` tracking iteration index, hypothesis formulation, targeted subtasks, and quantitative confidence progression.
  3. Upgrade `CriticAgent` to perform recursive evidentiary gap audits, emitting `unresolved_gaps`, targeted `gap_queries`, and testable `suggested_hypotheses`.
  4. Extend `PlannerAgent.replan()` to support deep iteration context, transforming gap queries into dynamically scheduled DAG subtasks with capability routing.
  5. Enforce 3 strict convergence guardrails:
     - Target confidence threshold ($\tau \ge 0.85$).
     - Hard iteration ceiling (`max_iterations`, default: 3, max: 5).
     - Diminishing returns cutoff ($\Delta \tau < 0.02$ across consecutive rounds).
  6. Define deep research event types (`DEEP_RESEARCH_STARTED`, `RESEARCH_ITERATION_STARTED`, `HYPOTHESIS_FORMULATED`, `RESEARCH_ITERATION_COMPLETED`, `DEEP_RESEARCH_CONVERGED`, `DEEP_RESEARCH_TERMINATED`) with real-time WebSocket broadcasting.
  7. Develop `DeepResearchTracker.tsx` in the React frontend with iteration timeline stepper, confidence convergence gauge, hypothesis status badges, and gap resolution tree.
- **Consequences**:
  - Positive: Autonomous self-refining research operating system eliminating manual prompt re-runs.
  - Positive: Complete transparency and deterministic termination guarantees preventing infinite execution loops or resource exhaustion.

---

## ADR 016: Persistent Cross-Session Research Memory & Conceptual Indexing (Phase 16)
- **Status**: Accepted & Implemented (September 2026)
- **Context**: Autonomous research workflows span multiple sessions, inquiries, and days. Without persistent cross-session memory, agents repeat identical background investigations, lose previously established findings, and cannot answer follow-up queries like *"Continue the research from where we stopped"* or *"How does this finding compare to our study on PLA polymers last week?"*.
- **Decision**:
  1. Define `DBResearchMemory` database model in `packages/database/src/database/models/memory.py` with dialect-safe `JSONType`, `GUID`, category types (`concept`, `finding`, `hypothesis`, `methodology`, `fact`), categorization tags, confidence score, provenance JSON, and access tracking (`access_count`, `last_accessed_at`).
  2. Implement `MemoryRepository` in `packages/database/src/database/repositories/memory_repository.py` providing transactional async CRUD, keyword/text search, and access frequency tracking.
  3. Implement `ResearchMemoryManager` in `packages/research/src/research/memory/manager.py` orchestrating:
     - Pre-planning recall (`recall_memories()`): Recalls top relevant historical memories for the user's research query and injects a structured memory summary into `PlannerAgent` context.
     - Post-synthesis auto-consolidation (`store_memories_from_report()`): Distills key findings, methodology summaries, and verified hypotheses from synthesized `ResearchReport` objects into persistent memory entries.
  4. Create agent memory tools (`RecallMemoryTool`, `StoreMemoryTool`) in `packages/tools/src/tools/definitions/memory.py` allowing autonomous in-flight memory queries and explicit memory storage by agents.
  5. Implement FastAPI REST endpoints (`/api/v1/memory`) supporting memory querying, text search, manual memory creation, partial updates, and deletion.
  6. Create interactive React components (`ResearchMemoryViewer.tsx` and `MemoryPage.tsx`) with dark glassmorphism theme, type badges, confidence gauges, tag filtering, access stats, and manual creation modals.
- **Consequences**:
  - Positive: Long-term continuity and knowledge accumulation across research sessions.
  - Positive: Eliminates redundant web search and document ingestion for previously answered sub-questions.
  ---

## ADR 017: Long-Term Knowledge Graph with Adjacency List Storage & GraphRAG (Phase 17)
- **Status**: Accepted & Implemented (September 2026)
- **Context**: While dense vector search and cross-session memory capture semantic similarity and text passages, complex scientific and competitive intelligence tasks require explicit entity-relation reasoning (e.g., *"Which organizations contributed to Transformer architectures, what datasets were used, and what methodologies were contradicted?"*). Vector similarity alone cannot perform multi-hop pathfinding or relational traversals across disparate documents.
- **Decision**:
  1. Implement persistent relational graph persistence in PostgreSQL 16 / SQLite using `DBKnowledgeEntity` and `DBKnowledgeRelation` models (`packages/database/src/database/models/graph.py`) with dialect-safe `GUID`, `JSONType`, entity categories (`CONCEPT`, `TECHNOLOGY`, `MATERIAL`, `PERSON`, `ORGANIZATION`, `METRIC`, `DATASET`, `PAPER`, `LOCATION`, `OTHER`), canonical name normalization, and relationship predicates (`AUTHORED_BY`, `USES_MATERIAL`, `CONTRADICTS`, `EVALUATED_ON`, `DEVELOPED_BY`, `CORRELATES_WITH`, `DERIVED_FROM`, `APPLIES_METHODOLOGY`, `EXPOSED_TO`, `HOSTS`, `SECRETES`, `ENHANCES`, `SYNTHESIZED_VIA`, `RELATES_TO`).
  2. Implement `KnowledgeGraphRepository` with BFS $k$-hop subgraph extraction, shortest-path multi-hop traversal, entity canonicalization, and batch triplet upserts.
  3. Adhere to **ADR 008** (avoiding premature Neo4j or external graph infrastructure) by implementing indexed adjacency lists in PostgreSQL/SQLite that execute sub-millisecond local traversals for tens of thousands of entity nodes.
  4. Implement `KnowledgeGraphEngine` in `packages/research/src/research/graph/engine.py` orchestrating:
     - Automated triplet extraction from research reports, papers, and text findings (`extract_triplets_from_text`, `extract_from_report`).
     - Graph-Augmented RAG (`get_graph_augmented_context`) injecting structured relational subgraphs and neighbor entity definitions into agent prompts.
     - Multi-hop relational pathfinding between arbitrary named entities (`find_path_between_entities`).
  5. Build and register agent graph tools in `packages/tools/src/tools/definitions/graph.py` (`QueryKnowledgeGraphTool`, `ExtractGraphTripletsTool`, `FindRelationPathTool`).
  6. Implement FastAPI REST routes (`/api/v1/graph`) supporting node/edge CRUD, k-hop subgraph extraction, multi-hop path queries, triplet extraction, and graph stats.
  7. Develop `KnowledgeGraphViewer.tsx` and `KnowledgeGraphPage.tsx` with interactive force-layout SVG network visualization, entity type color palettes, node inspector drawer, multi-hop pathfinder, and triplet extraction studio.
---

## ADR 018: Multi-Tenant Workspace & Project Hierarchy (Phase 18)
- **Status**: Accepted & Implemented (September 2026)
- **Context**: Multi-tenant research platforms require hierarchical resource isolation (`User -> Workspace -> Projects -> {Research Jobs, Documents, Memory, Knowledge Graph}`). Without workspace and project boundaries, documents, persistent memories, knowledge graphs, and research jobs from disparate domains or client engagements clash in flat global namespaces, creating risk of data contamination and preventing granular team access controls.
- **Decision**:
  1. Introduce `DBWorkspace`, `DBWorkspaceMember`, and `DBProject` database models in `packages/database/src/database/models/workspace.py` with dialect-safe `GUID`, `JSONType`, membership roles (`owner`, `admin`, `researcher`, `member`, `viewer`), and URL-safe collision-resistant slug generation.
  2. Extend existing models (`ResearchJob`, `Document`, `DBResearchMemory`, `DBKnowledgeEntity`) with `workspace_id` and `project_id` foreign keys and compound indexes.
  3. Implement `WorkspaceRepository` and `ProjectRepository` in `packages/database/src/database/repositories/` with automatic provisioning of personal default workspaces and projects, membership checks, and aggregated statistical overview queries (`total_jobs`, `total_documents`, `total_memories`, `total_graph_entities`).
  4. Implement dedicated REST API endpoints under `/api/v1/workspaces` and `/api/v1/projects` in `apps/api/src/api/routes/`.
  5. Upgrade `ResearchPipeline`, `IngestionPipeline`, and API routes (`/research`, `/documents`) to accept, propagate, and filter by `workspace_id` and `project_id`.
  6. Build `WorkspaceContext.tsx`, `WorkspaceSelector.tsx` dropdown switcher in the sidebar, and `ProjectsPage.tsx` management studio in `apps/web`.
- **Consequences**:
  - Positive: Clean hierarchical multi-tenancy and data isolation across all research artifacts.
  - Positive: Zero-breakage backward compatibility via nullable foreign keys and automated default workspace provisioning.
  - Positive: Sets the foundation for Phase 19 (Team Collaboration: Granular RBAC, Invitations, Shared Reports & Annotations).

---

## ADR 019: Team Collaboration, Workspace Invites, Report Annotations, and Activity Feed (Phase 19)
- **Status**: Accepted & Implemented (September 2026)
- **Context**: While Phase 18 established the physical workspace and project boundaries, researchers working in teams need streamlined invitation workflows (email tokens, role assignments), contextual peer review (inline paragraph annotations and thread resolution on synthesized reports), and an immutable collaborative activity audit log.
- **Decision**:
  1. Introduce `DBWorkspaceInvite`, `DBReportAnnotation`, and `DBWorkspaceActivity` database models in `packages/database/src/database/models/collaboration.py` with URL-safe crypto token generation (`generate_invite_token()`), expiration timestamps (7-day default), dialect-safe `GUID` and `JSONType`, and compound performance indexes (`ix_workspace_invites_ws_email`, `ix_report_annotations_report_status`, `ix_ws_activities_ws_created`).
  2. Implement `WorkspaceInviteRepository`, `ReportAnnotationRepository`, and `WorkspaceActivityRepository` in `packages/database/src/database/repositories/collaboration_repo.py` supporting:
     - Cryptographic invite generation, token lookup, idempotent token acceptance (upgrading/adding membership in `workspace_members`), and invite revocation.
     - Threaded report annotations with section indices, selected text quotes, resolution tracking (`resolved_by`, `resolved_at`), and author-only/admin deletion security guardrails.
     - Chronological activity stream logging and querying across workspaces and specific projects.
  3. Implement REST API endpoints in `apps/api/src/api/routes/collaboration.py`:
     - `/api/v1/workspaces/{id}/invites` (POST, GET)
     - `/api/v1/invites/{token}` (GET)
     - `/api/v1/invites/{token}/accept` (POST)
     - `/api/v1/invites/{id}` (DELETE)
     - `/api/v1/reports/{id}/annotations` (POST, GET)
     - `/api/v1/annotations/{id}/resolve` (PATCH)
     - `/api/v1/annotations/{id}` (DELETE)
     - `/api/v1/workspaces/{id}/activities` (GET)
     - `/api/v1/projects/{id}/activities` (GET)
  4. Build React collaboration interfaces:
     - `WorkspaceMembersModal.tsx`: Real-time member roster, role badges, email invitation form, invite link copy button, and pending invite revocation.
     - `ReportAnnotationsDrawer.tsx`: Slide-over review drawer on `ResearchDetail.tsx` with section quotes, comment threads, filter tabs (All, Open, Resolved), and 1-click resolution.
     - Integrated team access modal into `ProjectsPage.tsx`.
- **Consequences**:
  - Positive: Seamless multi-user peer review and team expansion without manual database interventions.
  - Positive: Complete auditability through immutable collaborative activity logs.

---

## ADR 020: Intelligent Model Ecosystem with Multi-Parameter Routing Optimization and Pareto-Frontier Selection (Phase 20)
- **Status**: Accepted & Implemented (September 2026)
- **Context**: In a multi-model environment combining local offline engines (Ollama) and cloud frontier models (Google Gemini 2.5 Pro/Flash, OpenAI), simple hardcoded tier preferences or naive priority ordering are insufficient for diverse research workflows. Certain tasks require extreme speed and zero latency (interactive querying, streaming), others require budget-first cost minimization, while deep synthesis tasks demand maximum frontier reasoning and million-token context windows. Selecting models without considering multi-parameter trade-offs leads to suboptimal resource allocation and budget waste.
- **Decision**:
  1. Implement `ModelEcosystemOptimizer` in `packages/ai/src/ai/router/optimizer.py` featuring:
     - Multi-parameter utility scoring formula:
       $$\text{Score}(M) = w_q \cdot Q(M) + w_s \cdot S(M) + w_c \cdot C(M) + w_l \cdot L(M)$$
       where $Q(M)$ is the reasoning/quality score, $S(M)$ is the execution speed score, $C(M)$ is the cost efficiency score, and $L(M)$ is the locality score.
     - Non-dominated Pareto frontier sorting across 3 key continuous dimensions (Quality, Speed, Cost Efficiency) to identify models offering strictly optimal trade-offs.
     - Hard constraint filtering (latency SLA ceilings `max_latency_ms`, cost ceilings `max_cost_per_1k`, `require_local`, and mandatory capabilities).
     - Automated trade-off explanation generation providing human-readable justification for the winning model.
  2. Define preset `OptimizationProfile` configurations in `PRESET_PROFILES`:
     - `BALANCED`: $w_q=0.35, w_s=0.25, w_c=0.30, w_l=0.10$
     - `COST_MINIMIZED`: $w_q=0.20, w_s=0.15, w_c=0.55, w_l=0.10$
     - `SPEED_MAXIMIZED`: $w_q=0.20, w_s=0.55, w_c=0.10, w_l=0.15$
     - `QUALITY_MAXIMIZED`: $w_q=0.75, w_s=0.10, w_c=0.10, w_l=0.05$
     - `CUSTOM`: Arbitrary user-defined weights.
  3. Upgrade `ModelRouter` (`packages/ai/src/ai/providers/router.py`) and `ModelGateway` (`packages/ai/src/ai/gateway/model_gateway.py`) to accept `routing_profile` parameters, pass profiles through completion/streaming, and include `routing_profile` metadata in observability telemetry.
  4. Implement REST API endpoints in `apps/api/src/api/routes/models.py`:
     - `GET /api/v1/models/profiles`: Returns preset profile weights and descriptions.
     - `POST /api/v1/models/optimize`: Simulates candidate model ranking, Pareto-frontier identification, and itemized rationale for a given task and profile.
  5. Build frontend UI in `apps/web/src/pages/NewResearch.tsx`:
     - Interactive profile selection cards (Balanced ⚖️, Deep Quality 🏆, Ultra Fast ⚡, Cost Efficient 💰).
     - Real-time simulation preview showing the estimated winning model, Pareto-optimal badge, and trade-off summary before launching research.
- **Consequences**:
  - Positive: Optimal allocation of inference budgets and compute resources across heterogeneous tasks.
  - Positive: Transparent explainability with Pareto-frontier verification for why each model was selected.
  - Positive: Sets the foundation for Phase 21 (Model Evaluation System: Automated Ground-Truth Benchmarking).



