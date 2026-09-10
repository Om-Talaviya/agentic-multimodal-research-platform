# Architecture Decision Records (ADR): decisions.md

This document records the key architectural, engineering, and product design decisions made throughout the lifecycle of the **Agentic Multimodal Research Platform**.

---

## ADR 001: Provider-Agnostic AI Architecture

- **Status**: Accepted & Implemented (Phase 1 & Phase 8A)
- **Context**: The platform requires support for local inference (Ollama) for data privacy as well as cloud inference (Google Gemini, OpenAI-compatible APIs) for intensive reasoning tasks. Directly coupling agent code to vendor SDKs creates tight coupling and vendor lock-in.
- **Decision**: Define protocol-based abstractions (`LLMProvider`, `VisionProvider`, `EmbeddingProvider`, `RerankerProvider`) in `packages/ai` and decouple all agent implementations from concrete SDKs.
- **Consequences**:
  - Positive: Seamless swapping and mocking of model backends without touching agent code.
  - Positive: High testability with zero network flakiness in automated test suites.
  - Negative: Requires maintaining common request/response schemas (`LLMRequest`, `LLMResponse`) that normalize across provider idiosyncrasies.

---

## ADR 002: ModelGateway → ModelRouter → ModelRegistry Subsystem (Phase 8A)

- **Status**: Accepted & Implemented (September 2026)
- **Context**: As multiple models and providers were introduced, agents needed dynamic selection based on required capabilities (e.g., vision, streaming, structured JSON output) rather than hardcoded model strings, with automatic fallback handling.
- **Decision**: Implement a four-tier architecture:
  1. `ModelRegistry`: Maintains model catalog, priority scores, and task suitability mappings.
  2. `ProviderRegistry`: Manages concrete provider instances and provider health checks.
  3. `ModelRouter`: Evaluates matching candidate models based on task type and capabilities.
  4. `ModelGateway`: High-level entry point that orchestrates routing, automatic fallback failover, latency tracking, and telemetry attachment.
- **Consequences**:
  - Positive: Transparent failover if a primary provider experiences transient rate limits (HTTP 429) or outages.
  - Positive: Single point of telemetry collection for token counting and latency observability.

---

## ADR 003: Migration to Official Google Gemini Provider & Removal of Web2API

- **Status**: Accepted & Implemented (September 2026 / Phase 7.3)
- **Context**: Early experimental prototyping used an unofficial `GeminiWeb2API` browser-scraping adapter. This was fragile, violated API terms, and lacked enterprise stability.
- **Decision**: Completely delete `gemini_web2api.py` and replace it with `ai.providers.gemini.GeminiProvider` using the official `google-genai` / REST API.
- **Consequences**:
  - Positive: Enterprise reliability, low latency, official streaming, and clean authentication via `GEMINI_API_KEY`.
  - Positive: Eliminated unstable browser automation dependencies.

---

## ADR 004: Persistent PostgreSQL User Authentication & Alembic Migrations

- **Status**: Accepted & Implemented (September 2026 / Phase 7.2)
- **Context**: Initial Phase 6 implementations utilized an in-memory user registry for prototype testing. Production deployments require persistent user credentials, auditability, and schema migration tracking.
- **Decision**: Introduce a dedicated `users` table in PostgreSQL (with SQLite compatibility), managed via Alembic (`001_create_users_table.py`), using PBKDF2-HMAC-SHA256 password hashing and JWT access/refresh token pairs.
- **Consequences**:
  - Positive: Production-ready user persistence, audit logs, and smooth database evolution via Alembic.
  - Positive: Retained backward-compatible fallback for in-memory testing environments.

---

## ADR 005: Bi-directional WebSocket Streaming with Snapshot Hydration

- **Status**: Accepted & Implemented (Phase 2 & Phase 7.1)
- **Context**: Polling REST endpoints for long-running research jobs (taking 30–120 seconds) causes excessive network traffic and delayed UI state updates.
- **Decision**: Implement a dedicated WebSocket endpoint (`/api/v1/research/{job_id}/ws`). On connection, the server immediately delivers a complete `snapshot` of the job, task DAG, sources, evidence, and report, followed by real-time domain events emitted from `ResearchEventBus`.
- **Consequences**:
  - Positive: Instantaneous UI updates for task transitions, live evidence discovery, and final report delivery.
  - Positive: Eliminated polling race conditions and improved user experience.

---

## ADR 006: Server-Side Request Forgery (SSRF) Hardening on Web Tools

- **Status**: Accepted & Implemented (Phase 4 / Phase 6)
- **Context**: The `WebFetchTool` allows autonomous agents to fetch external URLs. If unconstrained, an attacker could supply intranet URLs (e.g., `http://169.254.169.254/latest/meta-data` or `http://localhost:5432`) to exfiltrate internal credentials or pivot attacks.
- **Decision**: Enforce DNS pre-resolution and IP address validation in `packages/shared/security.py`. Explicitly reject Loopback (`127.0.0.0/8`, `::1`), RFC 1918 Private networks (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), Link-local (`169.254.0.0/16`, `fe80::/10`), and Multicast IP ranges.
- **Consequences**:
  - Positive: Robust defense against SSRF vulnerabilities during autonomous agent web browsing.

---

## ADR 007: Hybrid RAG with Reciprocal Rank Fusion (RRF)

- **Status**: Accepted & Implemented (Phase 5)
- **Context**: Pure dense vector search can miss exact keyword matches (e.g., specific part numbers, technical terms), while pure lexical search (BM25) fails on semantic synonyms.
- **Decision**: Implement `HybridRetriever` combining dense ChromaDB embeddings with sparse BM25 keyword scoring, merging candidates using Reciprocal Rank Fusion ($k=60$).
- **Consequences**:
  - Positive: Maximized retrieval recall and precision across diverse technical and scientific queries.
