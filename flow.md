# System & User Workflows: flow.md

This document specifies the end-to-end operational, agentic, data ingestion, model routing, and real-time streaming workflows of the **Agentic Multimodal Research Platform**.

---

## 1. Authentication & Session Flow

```mermaid
sequenceDiagram
    autonumber
    actor Client as User / Frontend
    participant API as FastAPI Auth (/api/v1/auth)
    participant DB as PostgreSQL (users)
    participant JWT as Auth Service

    Client->>API: POST /login {username, password}
    API->>DB: Query User by username or email
    DB-->>API: User record (password_hash, salt, role)
    API->>JWT: verify_password(password, password_hash)
    alt Password Valid & User Active
        JWT-->>API: Verified
        API->>JWT: create_access_token(user, exp=24h)
        API->>JWT: create_refresh_token(user, exp=7d)
        API-->>Client: HTTP 200 {access_token, refresh_token, user_profile}
    else Password Invalid or Inactive
        API-->>Client: HTTP 401 Unauthorized
    end

    opt Token Expiration & Refresh
        Client->>API: POST /token/refresh {refresh_token}
        API->>JWT: verify_token(refresh_token, expected_type="refresh")
        API-->>Client: HTTP 200 {access_token, refresh_token}
    end
```

---

## 2. Research Job Lifecycle & Agentic Execution Flow

```mermaid
flowchart TD
    A[Client Submits Question] -->|POST /api/v1/research| B[ResearchJob Created in DB]
    B --> C[Orchestrator Triggers PlannerAgent]
    C --> D[Planner Deconstructs Query into Task DAG]
    D --> E[Save Tasks in DB & Emit tasks_created Event]

    E --> F{Ready Tasks in DAG?}
    F -->|Yes| G[Spawn Worker Coroutines in Parallel]
    F -->|Dependencies Pending| H[Wait for Predecessor Completion]

    subgraph Agent Task Execution
        G --> I{Task Type}
        I -->|web_search| J[WebResearchAgent]
        I -->|document_analysis| K[DocumentAnalysisAgent]
        J --> L[WebSearch / SSRF-safe WebFetch]
        K --> M[Query Hybrid RAG Store]
        L --> N[Extract Raw Evidence & Sources]
        M --> N
    end

    N --> O[Save Sources & Evidence to DB]
    O --> P[CriticAgent Audits & Scores Evidence]
    P -->|Verification Completed| Q[Mark Task Completed in DB]
    Q --> F

    F -->|All Tasks Completed| R[ReportAgent Synthesizes Verified Findings]
    R --> S[Generate Final Report with Citations]
    S --> T[Mark ResearchJob COMPLETED]
    T --> U[Emit job_completed via WebSocket]
```

---

## 3. Multimodal Document Ingestion Flow

```mermaid
flowchart LR
    A[Document Upload] -->|POST /api/v1/documents| B[MIME Type Detection & Validation]
    B --> C{File Type}

    C -->|PDF| D[PDFParser: pdfplumber text & table extraction]
    C -->|DOCX| E[DocxParser: python-docx paragraph & table extraction]
    C -->|Image PNG/JPG| F[ImageParser: Vision LLM via ModelGateway]
    C -->|Markdown/Text| G[TextParser: UTF-8 normalization]

    D --> H[Semantic & Fixed Chunking]
    E --> H
    F --> H
    G --> H

    H --> I[Embedder: nomic-embed-text / Gemini]
    I --> J[(ChromaDB Vector Store)]
    H --> K[(BM25 Sparse Lexical Index)]
    H --> L[(PostgreSQL document_chunks)]
```

---

## 4. Hybrid RAG & Knowledge Retrieval Flow

```mermaid
sequenceDiagram
    autonumber
    participant Agent as Research Agent
    participant Retriever as HybridRetriever
    participant Vector as ChromaDB
    participant BM25 as BM25 Keyword Index
    participant RRF as Reciprocal Rank Fusion

    Agent->>Retriever: retrieve(query, top_k=10)
    par Dense Vector Search
        Retriever->>Vector: query_embeddings(query, k=20)
        Vector-->>Retriever: Ranked dense results
    and Sparse Lexical Search
        Retriever->>BM25: search(tokenize(query), k=20)
        BM25-->>Retriever: Ranked sparse results
    end
    Retriever->>RRF: Fuse ranked lists with k=60
    RRF-->>Retriever: Combined & deduplicated top_k chunks
    Retriever-->>Agent: Grounded evidence context with source metadata
```

---

## 5. Intelligent Model Routing & Fallback Failover Flow (Phase 8A / 8B)

```mermaid
sequenceDiagram
    autonumber
    participant Caller as Agent / Task Runner
    participant Gateway as ModelGateway
    participant Router as ModelRouter
    participant Reg as Model & Provider Registries
    participant P1 as Primary Model (e.g. Gemini / Ollama)
    participant P2 as Fallback Model (e.g. Local Fallback)

    Caller->>Gateway: complete(request, task=TaskType.SYNTHESIS)
    Gateway->>Router: select_model_and_provider(task=SYNTHESIS)
    Router->>Reg: Match capabilities, task suitability & priority
    Reg-->>Router: Selected (ModelDefinition, PrimaryProvider)
    Router-->>Gateway: Return Primary Provider

    Gateway->>P1: complete(request)
    alt Primary Provider Succeeded
        P1-->>Gateway: LLMResponse (with tokens, text)
        Gateway-->>Caller: LLMResponse + Telemetry Metadata
    else Primary Provider Fails (Timeout / Rate Limit / Error)
        P1--xGateway: ProviderUnavailableError
        Gateway->>Router: select_model_and_provider(exclude=[P1])
        Router-->>Gateway: Return Fallback Provider (P2)
        Gateway->>P2: complete(request)
        P2-->>Gateway: LLMResponse
        Gateway-->>Caller: LLMResponse + {fallback_occurred: true, original_model: P1}
    end
```

---

## 6. Live WebSocket Streaming Flow

```mermaid
sequenceDiagram
    autonumber
    actor Web as React Client
    participant WS as WebSocket Endpoint (/research/{id}/ws)
    participant Bus as ResearchEventBus
    participant DB as Database Session

    Web->>WS: Connect WebSocket (with JWT token)
    WS->>WS: Authenticate token & verify permissions
    WS->>Bus: Subscribe to job_id topic
    WS->>DB: Load current snapshot (Job, Tasks, Sources, Evidence, Report)
    WS-->>Web: Send type="snapshot" payload

    loop Real-Time Background Execution
        Bus->>WS: Push Domain Event (e.g. task_started, evidence_added)
        WS-->>Web: Send type="event" {event_type, data}
    end

    opt Heartbeat Keep-Alive
        WS-->>Web: Send type="heartbeat" every 30s
    end
```

---

## 7. Error Handling & Recovery Pathways

1. **Model Invocation Failure**:
   - `ModelGateway` attempts up to `max_fallback_attempts` (default: 1) against alternative eligible providers before propagating errors.
2. **Tool Failure (SSRF / Network Timeout)**:
   - `WebFetchTool` rejects unsafe targets immediately without network invocation.
   - Transient network fetch timeouts return empty result sets with error logs rather than crashing worker coroutines.
3. **Task Failure in DAG**:
   - If a non-critical task fails, dependent tasks are flagged as `failed` while independent branches continue uninterrupted.
   - The job error state is captured in `ResearchJob.error_message`.
