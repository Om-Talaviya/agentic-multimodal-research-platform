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

---

## ADR 021: Automated Model Evaluation System with Golden Benchmark Harness and Competitive Leaderboard (Phase 21)
- **Status**: Accepted & Implemented (September 2026)
- **Context**: In Phase 20, we built multi-parameter utility optimization and Pareto-frontier routing across models based on static catalog ratings and token costs. However, evaluating whether a model actually delivers high-quality reasoning, avoids hallucinations, accurately cites references, and follows multi-step logic requires an empirical, offline benchmark harness with ground-truth test cases. Without an automated evaluation framework, model upgrades and new provider integrations cannot be quantitatively verified for research fidelity.
- **Decision**:
  1. Implement a standardized multi-category golden benchmark suite in `packages/ai/src/ai/eval/schemas.py`:
     - `BenchmarkCategory`: `REASONING`, `FACTUAL_RETRIEVAL`, `SYNTHESIS`, `CITATION_ACCURACY`, `CODING`.
     - `BenchmarkSample`: Individual test cases containing inputs, reference contexts, expected keywords, reasoning step requirements, and expected citation keys.
     - `DEFAULT_RESEARCH_BENCHMARK`: Built-in 5-task multi-domain research benchmark dataset.
  2. Build `EvaluationMetricsEngine` in `packages/ai/src/ai/eval/metrics.py` computing deterministic quantitative metrics [0.0 - 1.0]:
     - Factual Accuracy: Keyword recall and precision against expected factual anchors.
     - Reasoning Depth: Step-marker regex density and deductive elaboration structure.
     - Retrieval Faithfulness: Context grounding vs. hallucination word ratio.
     - Citation Precision: Source tag match percentage.
     - Overall Composite Score: Weighted average ($35\%$ Factuality, $30\%$ Reasoning, $20\%$ Faithfulness, $15\%$ Citations).
  3. Implement `ModelEvaluator` (`packages/ai/src/ai/eval/evaluator.py`) to orchestrate benchmark runs through `ModelGateway` with temperature=0.1, timing latency, recording token counts, and generating `EvaluationReport`.
  4. Create database persistence layer in `packages/database/src/database/models/evaluation.py` and `packages/database/src/database/repositories/evaluation_repo.py`:
     - `DBModelEvaluation`: Stores top-level benchmark run summaries, mean metrics, pass rate, latency, and cost.
     - `DBModelBenchmarkResult`: Stores per-sample prompt, output, metrics breakdown, and failure diagnostic messages.
  5. Implement REST API endpoints in `apps/api/src/api/routes/evaluation.py`:
     - `POST /api/v1/models/evaluate`: Triggers an automated evaluation run on target model.
     - `GET /api/v1/models/evaluations`: Lists historical evaluation runs.
     - `GET /api/v1/models/evaluations/{id}`: Retrieves detailed test case breakdowns.
     - `DELETE /api/v1/models/evaluations/{id}`: Deletes evaluation run.
     - `GET /api/v1/models/leaderboard`: Aggregates active model rankings, scores, latencies, and Pareto-frontier flags.
  6. Build React interface in `apps/web/src/pages/ModelEvaluationPage.tsx`:
     - Competitive leaderboard table with score progress bars and Pareto optimal badges.
     - "Run Benchmark" modal to trigger runs against registered models.
     - Evaluation test case breakdown drawer showing prompts, completions, and ground-truth targets.
- **Consequences**:
  - Positive: Ground-truth empirical scoring of all models replaces subjective guesswork.
  - Positive: Seamless verification of new local/cloud LLMs before promoting them to production research pipelines.
  - Positive: Establishes the foundation for Phase 22 (Agent Evaluation).

---

## ADR 022: Autonomous Agent Evaluation and Hallucination Observability Engine (Phase 22)
- **Status**: Accepted & Implemented (September 2026)
- **Context**: While Phase 21 benchmarked individual LLM models against static ground-truth questions, autonomous multi-agent pipelines (Planner, WebSearch, DocReader, Critic, Report Synthesizer) execute complex dynamic DAGs where failures can stem from invalid tool invocations, poor plan decomposition, ungrounded claim generation, or low evidence coverage. To ensure enterprise-grade reliability and track model drift, the platform requires an autonomous evaluation engine that audits complete agent execution trajectories, step telemetries, and report hallucination rates.
- **Decision**:
  1. Implement `AgentEvaluator` in `packages/ai/src/ai/eval/agent_evaluator.py`:
     - `evaluate_plan_precision()`: Assesses DAG subtask relevance and diversity relative to research objective.
     - `evaluate_tool_accuracy()`: Calculates tool execution success rates across historical steps.
     - `evaluate_evidence_coverage()`: Verifies whether synthesized claims are supported by collected documents/snippets.
     - `evaluate_hallucination_rate()`: Estimates proportion of ungrounded sentences using n-gram overlap with retrieved evidence sources.
     - `evaluate_job_execution()`: Produces composite `AgentEvaluationScorecard` with step telemetry breakdowns.
  2. Implement database persistence in `packages/database/src/database/models/agent_evaluation.py` and `packages/database/src/database/repositories/agent_evaluation_repo.py`:
     - `DBAgentEvaluation`: Tracks top-level execution scorecards, execution times, token counts, costs, and findings audits.
     - `DBAgentStepMetric`: Tracks sequential agent actions, tool inputs/outputs, error logs, and latencies.
     - `AgentEvaluationRepository`: Provides CRUD, historical evaluation query methods, and system-wide aggregate metrics calculation.
  3. Implement REST API endpoints in `apps/api/src/api/routes/agent_evaluations.py`:
     - `POST /api/v1/agents/evaluate`: Evaluates an agent execution run or research job.
     - `GET /api/v1/agents/evaluations`: Lists historical evaluations filtered by agent or job.
     - `GET /api/v1/agents/evaluations/{id}`: Returns scorecard with step telemetry.
     - `DELETE /api/v1/agents/evaluations/{id}`: Deletes evaluation run.
     - `GET /api/v1/agents/metrics/summary`: Returns system-wide quality and hallucination KPIs.
  4. Build React interface in `apps/web/src/pages/AgentEvaluationPage.tsx`:
     - KPI scorecard headers (Overall Score, Plan Precision, Tool Accuracy, Evidence Coverage, Hallucination Rate).
     - Per-agent architecture status cards (PlannerAgent, WebSearchAgent, DocumentReaderAgent, CriticAgent, ReportAgent).
     - Historical evaluation runs table with score badges and 1-click execution modal.
     - Step telemetry inspector drawer showing step-by-step tool inputs, outputs, tokens, and latencies.
- **Consequences**:
  - Positive: Complete visibility into autonomous multi-agent reasoning quality and step execution health.
  - Positive: Empirical, automated tracking of hallucination rates across research reports.
  - Positive: Concludes Generation 5 (AI Platform Intelligence) and unlocks Generation 6: Phase 23 (Enterprise Security).

---

## ADR 023: Enterprise KMS Envelope Encryption, Cryptographic Audit Chains, and GDPR Data Lifecycle Controls (Phase 23)
- **Status**: Accepted & Implemented (September 2026)
- **Context**: As an enterprise-grade AI research operating system handling proprietary multi-tenant documents, corporate secrets (LLM API keys, database credentials), and compliance obligations (SOC 2 Type II, GDPR Article 17 Right-to-be-Forgotten), the platform required military-grade cryptographic protection. Storing plaintext secrets or mutable audit logs creates significant vulnerability to exfiltration or repudiation.
- **Decision**:
  1. Implement `KMSEnvelopeEncryption` in `packages/shared/src/shared/kms.py`:
     - Two-tier envelope encryption architecture: Master Key $\rightarrow$ PBKDF2-HMAC-SHA256 Key Encryption Key (KEK) $\rightarrow$ Ephemeral 256-bit Data Encryption Key (DEK) $\rightarrow$ AES-256-GCM authenticated payload encryption.
     - Protects sensitive credentials in `DBEncryptedSecret` with masked previews (`AIz...8877`) for secure UI management.
  2. Implement `AuditHashChainer` in `packages/shared/src/shared/kms.py`:
     - Tamper-evident cryptographic SHA-256 blockchain-like Merkle hash chaining across all security events:
       $$\text{CurrentHash} = \text{SHA256}(\text{PreviousHash} \parallel \text{Timestamp} \parallel \text{EventType} \parallel \text{ActorId} \parallel \text{ResourceId} \parallel \text{Details})$$
     - Cryptographic verification algorithm `verify_chain_integrity()` to detect broken links or modified records instantly.
  3. Implement database persistence in `packages/database/src/database/models/security.py` and `packages/database/src/database/repositories/security_repo.py`:
     - `DBSecurityAuditLog`: Stores immutable event logs with previous/current hash anchors.
     - `DBEncryptedSecret`: Stores AES-256-GCM encrypted payload and wrapped DEK with revocation controls.
     - `DBSecurityPolicy`: Configures per-workspace data retention days, MFA enforcement, IP whitelists, and data classification.
     - `execute_gdpr_data_purge()`: Implements automated cascade deletion and anonymization across research jobs, documents, memories, and graph entities under GDPR Article 17.
  4. Implement REST APIs in `apps/api/src/api/routes/security.py`:
     - `POST /api/v1/security/audit-logs`: Records hash-chained security event.
     - `GET /api/v1/security/audit-logs`: Queries audit trails.
     - `GET /api/v1/security/audit-logs/verify`: Cryptographically verifies SHA-256 hash chain integrity.
     - `POST /api/v1/security/secrets` & `GET /api/v1/security/secrets`: Vaults and lists secrets.
     - `PATCH /api/v1/security/secrets/{id}/revoke` & `DELETE /api/v1/security/secrets/{id}`: Secret lifecycle controls.
     - `GET /api/v1/security/policy` & `PATCH /api/v1/security/policy`: Workspace policy management.
     - `POST /api/v1/security/gdpr/purge`: Right-to-be-Forgotten data purge with strict confirmation validation.
     - `GET /api/v1/security/compliance/status`: Real-time SOC 2 & GDPR compliance scorecard.
  5. Build React interface in `apps/web/src/pages/EnterpriseSecurityPage.tsx`:
     - Compliance overview tab (SOC 2 Type II & GDPR live status cards with 1-click cryptographic integrity verification).
     - KMS Secret Vault tab (credential creation modal, provider filters, masked previews, revocation actions).
     - Immutable Audit Trail tab (log table with severity badges, SHA-256 hash anchors, and raw detail inspector).
     - Retention & GDPR tab (retention policy configuration, classification badges, and confirmation-gated data purge).
- **Consequences**:
  - Positive: Enterprise-grade SOC 2 and GDPR compliance readiness out of the box.
  - Positive: Tamper-evident cryptographic guarantees prevent audit log falsification.
  - Positive: Secure multi-tenant credential vaulting without plaintext exposure in database or network payloads.
  - Positive: Sets the security baseline for Phase 24 (Production Scale Infrastructure).

---

## ADR 024: Distributed Priority Task Queue, Asynchronous Worker Clusters, and S3/MinIO Blob Vault Architecture (Phase 24)
- **Status**: Accepted & Implemented (September 2026)
- **Context**: Scaling agentic multimodal research requires background asynchronous task processing capable of handling long-running multi-step research DAGs, heavy PDF/video/audio ingestion, and large dataset profiling without blocking HTTP request threads. Furthermore, large binary artifacts (multimodal evidence, high-resolution scientific charts, tabular datasets, generated PDF reports) require durable, presigned object storage rather than database storage.
- **Decision**:
  1. Implement `AsyncTaskQueue` & `WorkerNode` in `packages/research/src/research/workers/task_queue.py`:
     - Asynchronous priority min-heap queue supporting 4 priority levels (`CRITICAL`, `HIGH`, `DEFAULT`, `LOW`).
     - Task tracking with retry counters, error payloads, execution latency tracking, and timeout leases.
     - Worker node abstraction with capability tagging (`web_search`, `pdf_parsing`, `multimodal`, etc.), heartbeat leasing, and dynamic concurrency limits.
  2. Implement `ObjectStorageClient` in `packages/shared/src/shared/storage.py`:
     - Unified multi-provider abstraction supporting AWS S3, MinIO, and local filesystem backends.
     - Presigned URL generator for secure time-limited client upload/download (`generate_presigned_url`).
     - Automatic MD5 and SHA-256 checksum calculation, MIME type detection, and aggregate bucket usage telemetry.
  3. Implement Database Persistence in `packages/database/src/database/models/infrastructure.py` and `packages/database/src/database/repositories/infrastructure_repo.py`:
     - `DBWorkerNode`: Persistent cluster node registry with status (`ready`, `busy`, `draining`, `offline`), CPU/RAM metrics, and heartbeat leases.
     - `DBStorageObject`: Persistent metadata index for stored blobs with workspace scoping, storage class, ETag, and byte size.
  4. Implement REST APIs in `apps/api/src/api/routes/system_infra.py`:
     - `GET /api/v1/system/workers`: Cluster node listing and health statuses.
     - `POST /api/v1/system/workers/heartbeat`: Worker pulse and load telemetry.
     - `GET /api/v1/system/queue/status` & `POST /api/v1/system/queue/tasks`: Distributed priority task queue management.
     - `GET /api/v1/system/storage/objects`, `POST /api/v1/system/storage/presigned-url`, and `GET /api/v1/system/storage/usage`: Blob storage operations.
  5. Build React Interface in `apps/web/src/pages/ProductionInfrastructurePage.tsx`:
     - Cluster Topology tab (active nodes, CPU/RAM bars, heartbeat pulse simulator, drain/delete node actions).
     - Distributed Task Queue tab (queue metrics, priority breakdown, task enqueue modal, retry triggers).
     - S3/MinIO Blob Vault tab (object browser, storage class badges, presigned URL generator modal, aggregate storage usage cards).
- **Consequences**:
  - Positive: High-throughput background execution decoupled from HTTP request loops.
  - Positive: Scalable object storage for heavy multimodal media and enterprise reports.
  - Positive: Foundation ready for public developer API platform (Phase 25) and recurring research automation (Phase 26).

---

## ADR 025: Public API Gateway, SHA-256 Hashed API Keys, and Sliding Window Rate Limiting (Phase 25)
- **Status**: Accepted & Implemented (September 2026)
- **Context**: Enabling external platforms, autonomous bots, developer CLI tools, and enterprise integrations to harness the AI Research OS requires a standardized, secure programmatic API. The platform requires cryptographically secure API key management (never storing raw keys), fine-grained permission scopes to enforce the principle of least privilege, tier-based sliding window rate limiting to prevent abuse, and developer-friendly interactive playgrounds with ready-to-copy cURL, Python, and TypeScript SDK snippets.
- **Decision**:
  1. Implement `DBApiKey` in `packages/database/src/database/models/api_key.py`:
     - Secure storage with `key_prefix` (`amrp_live_...` for fast indexing) and `key_hash` (SHA-256 digest of secret token).
     - Granular permission scopes (`research:read`, `research:write`, `documents:read`, `documents:write`, `memory:read`, `graph:read`).
     - Tier and rate limit attributes (`rate_limit_tier`: `free`, `pro`, `enterprise`; `rate_limit_rpm`: 60, 300, 1,200).
     - Expiration tracking (`expires_at`) and last activity timestamp (`last_used_at`).
  2. Implement `ApiKeyRepository` in `packages/database/src/database/repositories/api_key_repo.py`:
     - Constant-time SHA-256 authentication (`authenticate_api_key`) and required scope verification.
     - Sliding 60-second window rate limiter (`check_rate_limit`) computing allowed status, remaining requests, and window reset seconds.
     - Key lifecycle management: `create_api_key`, `list_api_keys`, `get_api_key`, `revoke_api_key`, `delete_api_key`.
  3. Implement Public Developer REST API in `apps/api/src/api/routes/developer.py`:
     - Key management: `GET /api/v1/developer/keys`, `POST /api/v1/developer/keys`, `GET /api/v1/developer/keys/{id}`, `PATCH /api/v1/developer/keys/{id}/revoke`, `DELETE /api/v1/developer/keys/{id}`.
     - Public endpoints: `POST /api/v1/developer/research` (enqueue research), `GET /api/v1/developer/research/{id}` (poll progress and get reports), `POST /api/v1/developer/documents` (ingest text/documents), `GET /api/v1/developer/usage` (inspect token consumption).
  4. Build React Interface in `apps/web/src/pages/DeveloperPlatformPage.tsx`:
     - API Keys Vault tab (create key modal with scope/tier/expiration selection, one-time reveal modal for generated secret key, active keys table with revoke/delete actions).
     - API Playground & SDK tab (interactive endpoint selector, live cURL / Python `requests` / TypeScript `axios` SDK code generators, one-click copy).
     - Rate Limits & Quotas tab (tier comparison cards, rate limit parameters, enterprise SLA specifications).
- **Consequences**:
  - Positive: Safe programmatic access without risk of leaking plaintext secrets in database dumps or telemetry logs.
  - Positive: Sliding window rate limiting prevents denial-of-service and model quota exhaustion.
  - Positive: Frictionless developer experience with copy-paste SDK snippets and instant playground testing.
  - Positive: Enables Phase 26 (Research Automation) to invoke internal and public APIs seamlessly.

---

## ADR 026: Autonomous Research Automation, Cron Scheduling, and Novelty-Triggered Multi-Channel Alerting (Phase 26)
- **Status**: Accepted & Implemented (September 2026)
- **Context**: Autonomous intelligence in enterprise and scientific domains requires proactive topic monitoring rather than passive user prompt-and-response. Users need to schedule recurring research sweeps across academic repositories (arXiv), web sources, and local document collections; automatically detect emerging changes, new claims, or contradictions relative to prior research sweeps; and receive notifications via in-app feeds and third-party webhooks only when significant novelty or contradictory claims are detected.
- **Decision**:
  1. Implement Database Models in `packages/database/src/database/models/automation.py`:
     - `DBScheduledResearch`: Persistent schedule entity with query topic, cron expressions (e.g. `0 9 * * 1`), interval frequencies (e.g. `86400`), source filters (`["web", "arxiv", "documents"]`), routing profile (`balanced`, `cost_minimized`, etc.), novelty threshold $\tau_{\text{novel}} \in [0, 1]$, and alert channels (`["in_app", "email", "webhook"]`).
     - `DBResearchSweepResult`: Historical record of completed sweeps capturing findings summaries, novel claims, contradictory claims, sources crawled, computed novelty scores, and token execution metrics.
     - `DBAutomationAlert`: Dispatched alerts linking schedule, sweep result, recipient user ID, alert type (`novel_finding`, `contradiction`, `schedule_error`), and read/acknowledgment status.
  2. Implement `AutomationRepository` in `packages/database/src/database/repositories/automation_repo.py`:
     - Full CRUD for schedules: `create_schedule`, `get_schedule`, `list_schedules`, `update_schedule`, `pause_schedule`, `resume_schedule`, `delete_schedule`.
     - Sweep tracking and history: `record_sweep_result`, `list_sweep_results`.
     - Alert lifecycle: `create_alert`, `list_alerts`, `acknowledge_alert`.
     - Real-time aggregate KPI metrics: `get_automation_metrics`.
  3. Implement `ResearchAutomationEngine` in `packages/research/src/research/automation/engine.py`:
     - `compute_next_run(cron_expression, interval_seconds, from_time)`: Robust next-timestamp computation supporting standard 5-field cron parsing and interval offsets.
     - `detect_novelty(current_claims, prior_claims)`: Semantic claim normalization and diffing engine that extracts new claims, isolates contradictions, and computes normalized novelty intensity $\text{score} \in [0.0, 1.0]$.
     - `execute_scheduled_sweep(schedule_id)`: Autonomous sweep execution pipeline that retrieves prior sweep memory, compares findings, updates `last_run_at`/`next_run_at`, and dispatches alerts via in-app feeds and external webhooks when $\text{novelty} \ge \tau_{\text{novel}}$.
  4. Implement REST APIs in `apps/api/src/api/routes/automation.py`:
     - Schedules: `POST /api/v1/automation/schedules`, `GET /api/v1/automation/schedules`, `GET /api/v1/automation/schedules/{id}`, `PATCH /api/v1/automation/schedules/{id}/pause`, `PATCH /api/v1/automation/schedules/{id}/resume`, `DELETE /api/v1/automation/schedules/{id}`, `POST /api/v1/automation/schedules/{id}/trigger`.
     - Sweeps: `GET /api/v1/automation/schedules/{id}/sweeps`.
     - Alerts: `GET /api/v1/automation/alerts`, `PATCH /api/v1/automation/alerts/{id}/acknowledge`.
     - Metrics: `GET /api/v1/automation/metrics`.
  5. Build React Studio in `apps/web/src/pages/ResearchAutomationPage.tsx`:
     - Sweeps & Cron Schedules tab (active/paused cards, next run countdown badges, trigger sweep on-demand, pause/resume/delete actions, new schedule modal with frequency/profile/novelty sliders).
     - Sweep History & Diff Explorer tab (chronological sweep timeline, novel claim tags with green highlight, contradictory claim tags with red highlight, sources crawled, novelty score gauge).
     - Dispatched Alerts & Webhooks tab (unread alert cards, novelty score badges, 1-click acknowledge button, webhook test dispatcher).
- **Consequences**:
  - Positive: Transforms the platform from a reactive tool into a proactive autonomous research intelligence engine.
  - Positive: Prevents alert fatigue by triggering notifications only when newly discovered findings exceed the configured novelty threshold.
  - Positive: Concludes the final milestone (Phase 26) of Generation 6 and the entire 6-Generation Product Roadmap!






