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



