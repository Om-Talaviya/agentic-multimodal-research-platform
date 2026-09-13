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

---

## 8. Multi-Tenant Workspace & Project Hierarchy Flow (Phase 18)

```mermaid
sequenceDiagram
    autonumber
    actor User as Researcher
    participant UI as WorkspaceSelector & App.tsx
    participant Ctx as WorkspaceContext
    participant API as FastAPI (/api/v1/workspaces, /api/v1/projects)
    participant DB as PostgreSQL / SQLite (workspaces, projects, members)
    participant Pipe as ResearchPipeline & Ingestion

    Note over User, DB: 1. Workspace & Project Auto-Hydration
    User->>UI: Logs in to platform
    UI->>Ctx: Hydrate active workspace from localStorage or API
    Ctx->>API: GET /api/v1/workspaces
    API->>DB: Query user workspaces & membership
    alt No workspace exists
        API->>DB: Provision default "Username's Workspace" & "General Research" project
    end
    DB-->>API: Workspaces list
    API-->>Ctx: Set currentWorkspace & currentProject
    Ctx-->>UI: Populate WorkspaceSelector dropdown

    Note over User, DB: 2. Scoped Research Job Submission
    User->>UI: Submit inquiry with active project selected
    UI->>API: POST /api/v1/research {question, workspace_id, project_id}
    API->>DB: Validate user membership in workspace
    API->>Pipe: Initialize job tagged with workspace_id & project_id
    Pipe->>DB: Persist job, sources, evidence scoped to project
    DB-->>UI: Return scoped job stream

    Note over User, DB: 3. Scoped Document & Knowledge Isolation
    User->>UI: Upload multimodal PDF/audio/dataset
    UI->>API: POST /api/v1/documents {file, workspace_id, project_id}
    API->>Pipe: Chunk, extract, index chunks with project metadata
    API->>DB: Persist Document with workspace_id & project_id foreign keys

---

## 9. Team Collaboration & Peer Review Flow (Phase 19)

```mermaid
sequenceDiagram
    autonumber
    actor Alice as Workspace Owner (Alice)
    actor Bob as Peer Reviewer (Bob)
    participant UI as React UI (WorkspaceMembersModal / ReportDrawer)
    participant API as FastAPI (/api/v1/collaboration)
    participant DB as PostgreSQL / SQLite (invites, annotations, activities)

    Note over Alice, DB: 1. Workspace Team Invitation Flow
    Alice->>UI: Opens Team & Access Modal -> Enters Bob's email & role
    UI->>API: POST /api/v1/workspaces/{ws_id}/invites {email: "bob@company.com", role: "reviewer"}
    API->>DB: Generate crypto token, insert into workspace_invites
    API->>DB: Log activity "member_invited" in workspace_activities
    API-->>UI: Return invite link / token (/invites/{token})

    Note over Bob, DB: 2. Token Redemption & Member Join
    Bob->>UI: Clicks invite link
    UI->>API: POST /api/v1/invites/{token}/accept
    API->>DB: Verify token validity and expiration (+7 days)
    API->>DB: Upsert Bob into workspace_members (role: reviewer)
    API->>DB: Set invite.is_accepted = true
    API->>DB: Log activity "member_joined" in workspace_activities
    API-->>UI: Bob joined workspace successfully

    Note over Bob, DB: 3. Inline Report Annotations & Collaborative Review
    Bob->>UI: Opens ResearchDetail.tsx -> Clicks "Review Notes" drawer
    Bob->>UI: Highlights section & writes comment note
    UI->>API: POST /api/v1/reports/{report_id}/annotations {comment_text, selected_text, section_index}
    API->>DB: Insert into report_annotations (status: open)
    API-->>UI: Live annotation added to drawer

    Note over Alice, DB: 4. Comment Resolution
    Alice->>UI: Views review drawer on report
    Alice->>UI: Clicks "Resolve" on Bob's comment
    UI->>API: PATCH /api/v1/annotations/{id}/resolve
    API->>DB: Update status = "resolved", resolved_by = Alice, resolved_at = NOW()
    API-->>UI: Drawer updates comment state with resolution badge
```

---

## 10. Intelligent Model Ecosystem Optimization Flow (Phase 20)

```mermaid
sequenceDiagram
    autonumber
    actor User as Researcher
    participant UI as NewResearch.tsx (Profile Selector)
    participant API as FastAPI (/api/v1/models/optimize)
    participant Opt as ModelEcosystemOptimizer
    participant Reg as ModelRegistry
    participant GW as ModelGateway

    User->>UI: Selects Routing Profile (e.g., "Deep Quality" or "Cost Efficient")
    UI->>API: POST /api/v1/models/optimize {profile, task: "long_form_research"}
    API->>Reg: Query candidate models for task capabilities
    Reg-->>API: Candidate ModelDefinitions
    API->>Opt: optimize(candidates, profile, task)
    Opt->>Opt: 1. Calculate Quality, Speed, Cost, Locality utility scores
    Opt->>Opt: 2. Compute non-dominated Pareto frontier
    Opt->>Opt: 3. Apply profile weights & rank candidates
    Opt-->>API: OptimizationResult (selected model, ranking, Pareto status, rationale)
    API-->>UI: Return live preview simulation data
    UI-->>User: Renders live routing target badge and Pareto analysis

    User->>UI: Submits research inquiry
    UI->>GW: Execute pipeline with routing_profile
    GW->>Opt: Route agent requests using active profile weights
```

---

## 11. Model Evaluation & Benchmark Leaderboard Flow (Phase 21)

```mermaid
sequenceDiagram
    autonumber
    actor Admin as AI Engineer / Admin
    participant UI as ModelEvaluationPage.tsx
    participant API as FastAPI (/api/v1/models/evaluate)
    participant Evaluator as ModelEvaluator
    participant GW as ModelGateway
    participant Metrics as EvaluationMetricsEngine
    participant Repo as ModelEvaluationRepository
    participant DB as PostgreSQL / SQLite (model_evaluations, model_benchmark_results)

    Admin->>UI: Selects Model & clicks "Run Benchmark"
    UI->>API: POST /api/v1/models/evaluate {model_id: "gemini-2.0-flash"}
    API->>Evaluator: evaluate_model(model_id, DEFAULT_RESEARCH_BENCHMARK)
    
    loop For Each Golden Benchmark Sample (Reasoning, Factual, Faithfulness, Citations)
        Evaluator->>GW: complete(LLMRequest(prompt, context))
        GW-->>Evaluator: LLMResponse(content, latency_ms, tokens, cost_usd)
        Evaluator->>Metrics: evaluate_sample(response, sample)
        Metrics->>Metrics: Compute Factuality, Reasoning Depth, Faithfulness, Citations
        Metrics-->>Evaluator: SampleEvaluationResult(metrics, passed, score)
    end

    Evaluator->>Evaluator: Aggregate Mean Scores, Pass Rate, Total Cost, Category Scores
    Evaluator-->>API: EvaluationReport
    API->>Repo: create_evaluation(report, sample_results)
    Repo->>DB: INSERT into model_evaluations & model_benchmark_results
    DB-->>Repo: Saved records
    Repo-->>API: Persisted DBModelEvaluation
    API-->>UI: 201 Created (EvaluationSummary)
    
    UI->>API: GET /api/v1/models/leaderboard
    API->>Repo: get_latest_evaluations_per_model()
    API->>API: Compute Pareto frontier flags on leaderboard models
    API-->>UI: Ranked competitive leaderboard with Pareto badges
    UI-->>Admin: Displays updated ranking table & test case breakdown drawer
```

---

## 12. Agent Execution Evaluation & Observability Flow (Phase 22)

```mermaid
sequenceDiagram
    autonumber
    actor Dev as AI Engineer / System
    participant UI as AgentEvaluationPage.tsx
    participant API as FastAPI (/api/v1/agents)
    participant Evaluator as AgentEvaluator
    participant Repo as AgentEvaluationRepository
    participant DB as PostgreSQL / SQLite (agent_evaluations, agent_step_metrics)

    Dev->>UI: Selects Agent / Run & clicks "Evaluate Agent"
    UI->>API: POST /api/v1/agents/evaluate {agent_name, plan_tasks, step_telemetry, evidence_items, report_text}
    API->>Evaluator: evaluate_job_execution(job_id, agent_name, plan_tasks, objective, telemetry, evidence, report)
    
    rect rgb(20, 30, 45)
        Note over Evaluator: 1. Multi-Dimensional Metric Computation
        Evaluator->>Evaluator: evaluate_plan_precision(plan_tasks, objective)
        Evaluator->>Evaluator: evaluate_tool_accuracy(step_telemetry)
        Evaluator->>Evaluator: evaluate_evidence_coverage(evidence_items, claims)
        Evaluator->>Evaluator: evaluate_hallucination_rate(report_text, evidence_items)
        Evaluator->>Evaluator: Compute overall_score & synthesis_fidelity
    end

    Evaluator-->>API: AgentEvaluationScorecard
    API->>Repo: create_evaluation(scorecard, step_telemetry, evaluated_by)
    Repo->>DB: INSERT into agent_evaluations & agent_step_metrics
    DB-->>Repo: Saved evaluation record
    Repo-->>API: Persisted DBAgentEvaluation
    API-->>UI: 201 Created (Scorecard Details)

    UI->>API: GET /api/v1/agents/metrics/summary
    API->>Repo: get_agent_metrics_summary()
    Repo-->>API: Summary aggregates (mean score, avg hallucination rate, tokens, cost)
    API-->>UI: Live KPI cards update (System Hallucination Rate, Plan Precision, Tool Accuracy)
    UI-->>Dev: Displays Scorecard, Historical Trends, and Step Telemetry Inspector Drawer
```

---

## 13. Enterprise Security, KMS Envelope Vault & Cryptographic Audit Trail Flow (Phase 23)

```mermaid
sequenceDiagram
    autonumber
    actor SecAdmin as Security Officer / Admin
    participant UI as EnterpriseSecurityPage.tsx
    participant API as FastAPI (/api/v1/security)
    participant KMS as KMSEnvelopeEncryption
    participant Chainer as AuditHashChainer
    participant Repo as SecurityRepository
    participant DB as PostgreSQL / SQLite (security_audit_logs, encrypted_secrets)

    rect rgb(20, 30, 45)
        Note over SecAdmin, DB: 1. Two-Tier KMS Envelope Encryption (Store Secret)
        SecAdmin->>UI: Inputs API Key / Secret Plaintext
        UI->>API: POST /api/v1/security/secrets {name, provider, plaintext_value}
        API->>Repo: create_encrypted_secret(...)
        Repo->>KMS: encrypt_secret(plaintext_value)
        KMS->>KMS: Generate ephemeral 256-bit DEK
        KMS->>KMS: AES-256-GCM Encrypt plaintext with DEK
        KMS->>KMS: AES-256-GCM Encrypt DEK with KEK (derived from master key)
        KMS-->>Repo: EncryptedPayload + EncryptedDEK + KeyVersion
        Repo->>DB: INSERT into encrypted_secrets (masked_preview, ciphertexts)
        Repo->>Chainer: compute_record_hash(prev_hash, timestamp, "secret_stored", ...)
        Chainer-->>Repo: SHA-256 CurrentHash
        Repo->>DB: INSERT into security_audit_logs (previous_hash, current_hash)
        Repo-->>API: Persisted Secret Metadata (Masked Preview only)
        API-->>UI: 201 Created (Vaulted Successfully)
    end

    rect rgb(20, 45, 30)
        Note over SecAdmin, DB: 2. Tamper-Evident Merkle Hash Chain Verification
        SecAdmin->>UI: Clicks "Verify Cryptographic Chain"
        UI->>API: GET /api/v1/security/audit-logs/verify
        API->>Repo: verify_audit_log_integrity(limit=500)
        Repo->>DB: SELECT security_audit_logs ORDER BY created_at ASC
        DB-->>Repo: Ordered Audit Records
        Repo->>Chainer: verify_chain_integrity(records)
        loop For Each Audit Record Link
            Chainer->>Chainer: Assert record[i].previous_hash == record[i-1].current_hash
            Chainer->>Chainer: Recompute SHA-256(prev | ts | event | actor | details)
            Chainer->>Chainer: Assert recomputed_hash == record[i].current_hash
        end
        Chainer-->>Repo: (is_valid=True, error=None)
        Repo-->>API: {verified: True, integrity_status: "VALID_TAMPER_EVIDENT", total_records: N}
        API-->>UI: Displays Verified Green Badge & Genesis Anchor
    end
```

---

## 14. Distributed Worker Task Queue & Blob Storage Flow (Phase 24)

```mermaid
sequenceDiagram
    autonumber
    actor User as Researcher / System
    participant UI as ProductionInfrastructurePage.tsx
    participant API as FastAPI (/api/v1/system)
    participant Queue as AsyncTaskQueue (Priority Heap)
    participant Worker as WorkerNode (Distributed Agent Pool)
    participant Storage as ObjectStorageClient (S3 / MinIO / Local)
    participant Repo as InfrastructureRepository
    participant DB as PostgreSQL / SQLite (worker_nodes, storage_objects)

    rect rgb(20, 30, 45)
        Note over User, DB: 1. Priority Task Enqueueing & Worker Dispatch
        User->>UI: Enqueues Heavy Research Task (Priority: CRITICAL)
        UI->>API: POST /api/v1/system/queue/tasks {task_name, payload, priority: "CRITICAL"}
        API->>Queue: enqueue(task_name, payload, priority=Priority.CRITICAL)
        Queue->>Queue: Push to Priority Min-Heap (CRITICAL -> HIGH -> DEFAULT -> LOW)
        Queue-->>API: QueuedTask (task_id, status="queued")
        API-->>UI: 201 Created (task_id)

        Worker->>Queue: dequeue()
        Queue-->>Worker: Dispatches QueuedTask
        Worker->>Repo: update_worker_heartbeat(node_id, status="busy", current_task_id=task_id)
        Repo->>DB: UPDATE worker_nodes SET status='busy', active_task_count=active_task_count+1
    end

    rect rgb(20, 45, 30)
        Note over Worker, Storage: 2. Multimodal Artifact Persistence (Object Storage Vault)
        Worker->>Worker: Executes Task & Generates Large Report / PDF / Dataset Artifact
        Worker->>Storage: put_object(bucket="research-artifacts", key="reports/job_99.pdf", data)
        Storage->>Storage: Compute MD5 & SHA-256 Checksums
        Storage->>Storage: Write to S3 / MinIO / Local FS
        Storage-->>Worker: StorageObjectMetadata (etag, size_bytes, backend_type)
        Worker->>Repo: record_storage_object(object_id, bucket, key, content_type, size, etag)
        Repo->>DB: INSERT into storage_objects
        Worker->>Queue: mark_completed(task_id, result_summary)
        Worker->>Repo: update_worker_heartbeat(node_id, status="ready", current_task_id=None)
    end

    rect rgb(45, 30, 20)
        Note over User, Storage: 3. Secure Presigned Retrieval
        User->>UI: Requests Download Link for Artifact
        UI->>API: POST /api/v1/system/storage/presigned-url {bucket, key, method: "GET"}
        API->>Storage: generate_presigned_url(bucket, key, method="GET", expires_in=3600)
        Storage-->>API: Presigned Signed URL with Expiry
        API-->>UI: {url: "https://minio.local/research-artifacts/reports/job_99.pdf?..."}
        UI-->>User: Initiates direct secure stream download
    end
```

---

## 15. Developer API Gateway & Key Authentication Flow (Phase 25)

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Third-Party Developer / Client App
    participant GW as FastAPI Public Gateway (/api/v1/developer/*)
    participant RateLimiter as ApiKeyRepository (Sliding Window)
    participant Auth as ApiKeyAuthenticator
    participant DB as PostgreSQL / SQLite (api_keys)
    participant Pipe as ResearchPipeline & WorkerPool

    rect rgb(20, 30, 45)
        Note over Dev, DB: 1. API Key Provisioning (Developer Studio UI)
        Dev->>GW: POST /api/v1/developer/keys {name: "Backend Bot", tier: "pro", scopes: ["research:write"]}
        GW->>GW: Generate Secret `amrp_live_<48_hex>` & Extract Prefix `amrp_live_...`
        GW->>GW: Compute Cryptographic SHA-256 Digest
        GW->>DB: INSERT into api_keys (key_prefix, key_hash, scopes, rate_limit_rpm=300)
        DB-->>GW: DBApiKey Record
        GW-->>Dev: 201 Created {secret_key: "amrp_live_...", key_prefix: "...", scopes: [...]} (One-time reveal)
    end

    rect rgb(20, 45, 30)
        Note over Dev, Pipe: 2. Programmatic Research Invocation & Rate Limit Verification
        Dev->>GW: POST /api/v1/developer/research (Header: X-API-Key: amrp_live_...)
        GW->>Auth: authenticate_api_key(raw_key, required_scope="research:write")
        Auth->>Auth: Extract Prefix -> SHA-256(raw_key)
        Auth->>DB: SELECT * FROM api_keys WHERE key_prefix = ... AND key_hash = ... AND is_active = True
        DB-->>Auth: DBApiKey Record
        Auth->>Auth: Verify required_scope in scopes
        Auth->>RateLimiter: check_rate_limit(key_id, limit_rpm=300)
        RateLimiter->>RateLimiter: Sliding 60-second request window check
        RateLimiter-->>Auth: (Allowed=True, Remaining=299, Reset=58s)
        Auth-->>GW: Authenticated Key Context (user_id, workspace_id, tier)

        GW->>Pipe: Enqueue autonomous research job
        Pipe-->>GW: JobQueued (job_id, status="pending")
        GW-->>Dev: 200 OK {job_id, status: "pending", poll_url: "/api/v1/developer/research/:id"}
    end

    rect rgb(45, 30, 20)
        Note over Dev, GW: 3. Programmatic Report Retrieval
        Dev->>GW: GET /api/v1/developer/research/{job_id} (Header: X-API-Key)
        GW->>Auth: authenticate_api_key(raw_key, required_scope="research:read")
        Auth-->>GW: Key Authenticated
        GW->>DB: Query research_jobs and reports
        DB-->>GW: DBReport Record
        GW-->>Dev: 200 OK {job_id, status: "completed", report: {title, findings, citations}}
    end
```

---

## 16. Research Automation, Scheduled Sweeps & Novelty Alerting Flow (Phase 26)

```mermaid
sequenceDiagram
    autonumber
    actor User as Researcher / Lead
    participant UI as ResearchAutomationPage.tsx
    participant API as FastAPI (/api/v1/automation)
    participant Engine as ResearchAutomationEngine
    participant Repo as AutomationRepository
    participant DB as PostgreSQL / SQLite (scheduled_research, research_sweep_results, automation_alerts)
    participant Webhook as Third-Party Webhook Receiver

    rect rgb(20, 30, 45)
        Note over User, DB: 1. Schedule Creation & Next Run Calculation
        User->>UI: Configures Scheduled Sweep (Cron / Interval, Sources, Novelty Threshold)
        UI->>API: POST /api/v1/automation/schedules {title, query, cron_expression, novelty_threshold: 0.35, alert_channels: ["in_app", "webhook"]}
        API->>Engine: compute_next_run(cron_expression, interval_seconds)
        Engine-->>API: next_run_at timestamp
        API->>Repo: create_schedule(user_id, title, query, cron, interval, novelty_threshold, next_run_at, ...)
        Repo->>DB: INSERT into scheduled_research
        DB-->>Repo: DBScheduledResearch
        Repo-->>API: Persisted Schedule Record
        API-->>UI: 201 Created (Schedule Active)
    end

    rect rgb(20, 45, 30)
        Note over Engine, DB: 2. Autonomous Sweep Execution & Semantic Claim Diffing
        Note over Engine: Scheduled Trigger Fired / On-Demand Manual Trigger
        API->>Engine: execute_scheduled_sweep(schedule_id)
        Engine->>Repo: get_schedule(schedule_id)
        Repo-->>Engine: DBScheduledResearch
        Engine->>Engine: Run autonomous research pipeline (retrieve papers, web findings, citations)
        Engine->>Repo: list_sweep_results(schedule_id, limit=5)
        Repo-->>Engine: Historical Prior Sweeps
        Engine->>Engine: detect_novelty(current_claims, prior_claims)
        Note over Engine: Computes novel_claims, contradictory_claims, and novelty_score in [0.0, 1.0]
        Engine->>Repo: record_sweep_result(schedule_id, findings_summary, novel_claims, contradictory_claims, novelty_score, ...)
        Repo->>DB: INSERT into research_sweep_results & UPDATE scheduled_research.last_run_at
        DB-->>Repo: DBResearchSweepResult
    end

    rect rgb(45, 30, 20)
        Note over Engine, Webhook: 3. Novelty Threshold Alerting & Webhook Dispatch
        alt novelty_score >= novelty_threshold OR contradictory_claims detected
            Engine->>Repo: create_alert(schedule_id, sweep_id, user_id, alert_type="novel_finding", title, summary, novelty_score, channel="in_app")
            Repo->>DB: INSERT into automation_alerts
            alt "webhook" in alert_channels AND webhook_url is configured
                Engine->>Webhook: POST webhook_url {event: "automation.alert", schedule_title, novel_claims, novelty_score}
                Webhook-->>Engine: 200 OK
            end
        end
        Engine-->>API: Sweep Execution Summary
        API-->>UI: Live Alert Count & Sweep Timeline Updated
    end
```
