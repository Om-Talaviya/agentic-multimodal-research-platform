# System & User Workflows: flow.md

This document specifies the end-to-end operational, agentic, data ingestion, model routing, and real-time streaming workflows of the **Agentic Multimodal Research Platform (AI Research OS)**.

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

## 2. Research Job Lifecycle & Real-Time Progression Flow

When a research query is submitted, the platform executes an end-to-end streamed pipeline:

```mermaid
flowchart TD
    A[Client Submits Research Inquiry] -->|POST /api/v1/research| B[ResearchJob Created with User ID]
    B --> C[Orchestrator Initializes Pipeline]
    
    subgraph Live Streaming Progression
        C --> D[1. Understanding Request]
        D --> E[2. Planning & Decomposing Subquestions]
        E --> F[3. Checking Private Knowledge Base]
        F --> G[4. Retrieving Relevant Documents]
        G --> H[5. Conducting External Web Research]
        H --> I[6. Analyzing Academic Papers & Tables]
        I --> J[7. Analyzing Data & Statistics with Deterministic Tools]
        J --> K[8. Comparing Evidence & Cross-Checking Claims]
        K --> L[9. Identifying Contradictions & Uncertainties]
        L --> M[10. Critic Review & Confidence Scoring]
    end

    M --> N{Critic: Evidence Sufficient?}
    N -->|No: Gaps Found| O[Recursive Loop: Planner Schedules Follow-up Tasks]
    O --> H
    N -->|Yes: Verified| P[11. Synthesizing Final Intelligence Report]
    P --> Q[12. Research Completed & Streamed over WebSocket]
```

---

## 3. User Context & Quota-Locked Model Routing Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as Authenticated User
    participant EP as Research Endpoint
    participant Pipe as ResearchPipeline
    participant Orch as AgentOrchestrator
    participant Agent as Specialized Agent
    participant GW as ModelGateway
    participant Quota as UserQuota Table (DB)
    participant Router as ModelRouter
    participant Prov as Model Provider (Ollama / Gemini / OpenAI)
    participant Usage as UsageRepository

    User->>EP: POST /api/v1/research {question} (JWT Header)
    EP->>Pipe: run(question, user_id=current_user.id)
    Pipe->>Orch: execute(job, user_id)
    Orch->>Agent: execute_task(task, AgentContext(user_id=user_id))
    Agent->>GW: complete(prompt, task_type, user_id)
    
    critical Row-Locked Quota Check
        GW->>Quota: SELECT ... FOR UPDATE WHERE user_id = :uid
        Quota-->>GW: Quota State (tokens_used, token_limit, cost_used)
    end
    
    alt Quota Exceeded
        GW->>Router: Request Zero-Cost / Local Fallback Model
        Router-->>GW: Fallback Ollama Model
    else Quota Available
        GW->>Router: select_model(task_type, constraints)
        Router-->>GW: Optimal Model Target
    end

    GW->>Prov: invoke_model(prompt, stream=False)
    Prov-->>GW: LLMResponse(content, token_usage, latency)
    
    GW->>Usage: record_usage(user_id, job_id, model, tokens, cost)
    Usage->>Quota: UPDATE user_quotas SET tokens_used = tokens_used + n
    GW-->>Agent: LLMResponse
```

---

## 4. Phase 9: Automated Knowledge Ingestion Pipeline Flow

```mermaid
flowchart LR
    Upload[Document Upload: PDF/DOCX/Image] --> Validate[MIME & Security Validation]
    Validate --> Extract[Structure & Table Extraction]
    Extract --> Normalize[Text Normalization]
    Normalize --> Chunk[Semantic Overlapping Chunking]
    Chunk --> Embed[Dense Vector Embedding]
    Chunk --> BM25[BM25 Sparse Tokenization]
    Embed --> Chroma[(ChromaDB Vector Store)]
    BM25 --> BM25Store[(Sparse Index)]
    Chroma --> Ready[Status: READY for Research Retrieval]
    BM25Store --> Ready
```

---

## 5. Explainability & Provenance Verification Flow

When a user asks: *"Why do you believe this finding?"*, the platform traverses the explicit provenance tree:

```
  Synthesized Report Finding
               │
               ▼
  Extracted Atomic Claim & Verification Confidence
               │
               ▼
  Exact Supporting Quote & Page/Coordinate Coordinates
               │
               ▼
  Source Document (PDF Table / Academic Preprint / Scraped Web URL)
               │
               ▼
  Raw Ingested Multimodal Chunk & Ingestion Timestamp
```

---

## 6. Phase 15: Deep Research Multi-Round Hypothesis Loop Flow

```mermaid
sequenceDiagram
    autonumber
    participant User as Researcher / Web UI
    participant DRE as DeepResearchEngine
    participant DAG as PipelineDAG / ToolExecutor
    participant Critic as CriticAgent
    participant Planner as PlannerAgent
    participant Rep as ReportAgent
    participant WS as WebSocket Broadcaster

    User->>DRE: start_deep_research(query, config: max_iter=3, target_tau=0.85)
    DRE->>WS: DEEP_RESEARCH_STARTED

    loop Iterative Hypothesis & Verification Loop (Round 1..N)
        DRE->>WS: RESEARCH_ITERATION_STARTED(round_idx)
        DRE->>DAG: execute_dag_subtasks(active_tasks)
        DAG-->>DRE: TaskResults & Ingested Evidence

        DRE->>Critic: critique_evidence_coverage(evidence, claims, current_hypotheses)
        Critic-->>DRE: CriticEvaluation(confidence_score, unresolved_gaps, gap_queries, suggested_hypotheses)

        alt Convergence Met (confidence >= target_tau OR delta_tau < 0.02 OR round >= max_iter)
            DRE->>WS: DEEP_RESEARCH_CONVERGED(tau, final_round)
            Note over DRE: Terminate loop immediately
        else Evidentiary Gaps or Low Confidence Detected
            DRE->>Planner: replan(gaps=gap_queries, hypotheses=suggested_hypotheses, iteration=round+1)
            Planner-->>DRE: DynamicSubtasks(is_dynamic=True, priority=High)
            DRE->>WS: HYPOTHESIS_FORMULATED(new_hypotheses, scheduled_tasks)
        end
    end

    DRE->>Rep: synthesize_deep_report(all_iterations, citations, confidence_trajectory)
    Rep-->>DRE: Comprehensive Deep Research Report
    DRE->>WS: DEEP_RESEARCH_TERMINATED(final_report)
    DRE-->>User: ResearchReport with Full Iteration History
```

---

## 7. Phase 16: Research Memory Recall & Auto-Consolidation Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as Researcher
    participant Pipe as ResearchPipeline
    participant MemMgr as ResearchMemoryManager
    participant MemRepo as MemoryRepository
    participant Planner as PlannerAgent
    participant Agents as Specialized Agents / Tools
    participant Rep as ReportAgent
    participant WS as WebSocket Broadcaster

    User->>Pipe: run(question, user_id)
    
    rect rgb(20, 30, 45)
        Note over Pipe, MemRepo: 1. Cross-Session Memory Recall
        Pipe->>MemMgr: recall_memories(user_id, query=question, limit=5)
        MemMgr->>MemRepo: search_by_text(user_id, query, limit=5)
        MemRepo-->>MemMgr: List[DBResearchMemory]
        MemMgr->>MemRepo: increment_access(memory_ids)
        MemMgr-->>Pipe: MemoryRecallResult(memories, summary)
        Pipe->>WS: MEMORY_RECALLED(count, titles)
        Pipe->>Planner: plan(question, context, historical_memories=recalled_summary)
    end

    Note over Planner, Agents: 2. Autonomous DAG Execution
    Planner-->>Pipe: ResearchPlan (incorporating prior knowledge)
    Pipe->>Agents: Execute DAG subtasks
    opt In-Flight Agent Memory Tool Calls
        Agents->>MemMgr: RecallMemoryTool / StoreMemoryTool
        MemMgr-->>Agents: Memory contents / Confirmation
    end
    Agents-->>Pipe: Verified Evidence & Findings

    rect rgb(20, 45, 30)
        Note over Pipe, MemRepo: 3. Post-Report Auto-Consolidation
        Pipe->>Rep: generate_report(evidence, query)
        Rep-->>Pipe: Synthesized ResearchReport
        Pipe->>MemMgr: store_memories_from_report(user_id, job_id, report)
        MemMgr->>MemRepo: batch_create(distilled_findings, methodologies, hypotheses)
        MemRepo-->>MemMgr: List[DBResearchMemory] persisted
        Pipe->>WS: MEMORY_STORED(count, keys)
    end

    Pipe-->>User: Final Research Job Complete (Memory Retained for Future Jobs)
```

---

## 7. Knowledge Graph Extraction & GraphRAG Flow (Phase 17)

```mermaid
sequenceDiagram
    autonumber
    actor User as Researcher
    participant Pipe as ResearchPipeline
    participant GraphEng as KnowledgeGraphEngine
    participant GraphRepo as KnowledgeGraphRepository
    participant DB as PostgreSQL / SQLite (knowledge_entities, knowledge_relations)
    participant Agent as Specialized Agent (Doc / Web / Report)
    participant UI as KnowledgeGraphViewer.tsx

    Note over Pipe, DB: 1. Graph-Augmented RAG (GraphRAG Context)
    Pipe->>GraphEng: get_graph_augmented_context(query, user_id, max_hops=2)
    GraphEng->>GraphRepo: find_entity_by_name(query)
    GraphRepo->>DB: SELECT * FROM knowledge_entities
    DB-->>GraphRepo: Root Entity
    GraphEng->>GraphRepo: get_k_hop_subgraph(entity_id, max_hops=2)
    GraphRepo->>DB: BFS Adjacency Traversal (nodes + edges)
    DB-->>GraphRepo: Subgraph nodes & edges
    GraphRepo-->>GraphEng: Subgraph data
    GraphEng-->>Pipe: Formatted Graph Context Text + Subgraph
    Pipe->>Agent: Prompt injected with Graph Context (Entities & Relations)

    Note over Agent, DB: 2. Agent Graph Tool Execution
    Agent->>GraphEng: FindRelationPathTool(source="Transformer", target="GPT-4")
    GraphEng->>GraphRepo: find_shortest_path(src_id, tgt_id, max_depth=4)
    GraphRepo-->>GraphEng: GraphPathResult(path_found=True, hops=2)
    GraphEng-->>Agent: Shortest Relational Path

    Note over Pipe, DB: 3. Post-Synthesis Triplet Extraction
    Pipe->>GraphEng: extract_from_report(user_id, job_id, report)
    GraphEng->>GraphEng: Parse entities & relation triplets from findings
    GraphEng->>GraphRepo: batch_upsert_triplets(triplets, user_id, job_id)
    GraphRepo->>DB: Upsert entities & relations with transaction commit
    DB-->>GraphRepo: Persisted count

    Note over UI, DB: 4. Real-time Interactive Graph Studio
    UI->>GraphRepo: GET /api/v1/graph/subgraph?center_entity_id={id}
    GraphRepo-->>UI: {nodes, edges, center_id} (Render force layout canvas)
```

