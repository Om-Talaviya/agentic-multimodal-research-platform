# Database Schema & API Contracts: backend-schema.md

This document defines the physical relational database schema, SQLAlchemy models, Alembic migrations, indexes, constraints, and API data contracts for the **Agentic Multimodal Research Platform**.

---

## 1. Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    users ||--o{ user_quotas : has
    users ||--o{ usage_records : incurs
    users ||--o{ research_jobs : creates
    users ||--o{ research_memories : owns
    
    research_jobs ||--o{ research_tasks : contains
    research_jobs ||--o{ sources : references
    research_jobs ||--o{ evidence : produces
    research_jobs ||--o{ documents : ingests
    research_jobs ||--o{ reports : synthesizes
    research_jobs ||--o{ agent_runs : executes
    research_jobs ||--o{ usage_records : attributes
    research_jobs ||--o{ research_memories : persists

    sources ||--o{ evidence : extracts
    documents ||--o{ document_chunks : splits
    agent_runs ||--o{ model_calls : logs

    users {
        UUID id PK
        String username UK
        String email UK
        String password_hash
        String role
        Boolean is_active
        DateTime created_at
        DateTime updated_at
    }

    user_quotas {
        UUID id PK
        UUID user_id FK,UK
        BigInteger token_limit
        BigInteger tokens_used
        Numeric cost_limit
        Numeric cost_used
        DateTime reset_at
        DateTime updated_at
    }

    usage_records {
        UUID id PK
        UUID user_id FK
        UUID job_id FK
        UUID task_id
        String provider
        String model
        Integer input_tokens
        Integer output_tokens
        Integer total_tokens
        Numeric estimated_cost
        Float latency_ms
        DateTime created_at
    }

    research_jobs {
        UUID id PK
        UUID user_id FK
        UUID request_id
        Text question
        Text objective
        String domain
        Text scope
        JSONB constraints
        String expected_output
        String status
        Text error_message
        DateTime started_at
        DateTime created_at
        DateTime updated_at
        DateTime completed_at
    }

    research_tasks {
        UUID id PK
        UUID job_id FK
        String type
        Text objective
        JSONB context
        String agent
        JSONB inputs
        JSONB depends_on
        Integer priority
        String status
        JSONB result
        Text error_message
        Integer retry_count
        DateTime created_at
        DateTime updated_at
    }

    sources {
        UUID id PK
        UUID job_id FK
        String url
        String title
        String source_type
        JSONB metadata_json
        DateTime created_at
    }

    evidence {
        UUID id PK
        UUID job_id FK
        UUID source_id FK
        Text claim
        Text supporting_quote
        Float confidence
        String verification_status
        JSONB metadata_json
        DateTime created_at
    }

    documents {
        UUID id PK
        UUID job_id FK
        String filename
        String file_path
        String mime_type
        Integer file_size
        String status
        JSONB metadata_json
        DateTime created_at
    }

    document_chunks {
        UUID id PK
        UUID document_id FK
        Integer chunk_index
        Text content
        JSONB metadata_json
        DateTime created_at
    }

    reports {
        UUID id PK
        UUID job_id FK
        Text title
        Text executive_summary
        JSONB methodology
        JSONB key_findings
        JSONB evidence_summary
        JSONB contradictions
        JSONB conclusions
        JSONB limitations
        Float confidence_score
        JSONB metadata_json
        DateTime created_at
    }
```

---

## 2. Relational Table Specifications

### 2.1 Table: `users`
- Managed via Alembic migration `001_create_users_table.py`.
- Primary storage for authenticated user credentials and RBAC roles.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | Unique user identifier |
| `username` | `VARCHAR(50)` | `UNIQUE, NOT NULL` | Unique user handle |
| `email` | `VARCHAR(255)` | `UNIQUE, NOT NULL` | Verified email address |
| `password_hash` | `VARCHAR(255)` | `NOT NULL` | PBKDF2-HMAC-SHA256 hashed password |
| `role` | `VARCHAR(20)` | `NOT NULL, DEFAULT 'Researcher'` | Role (`Admin`, `Researcher`, `Viewer`) |
| `is_active` | `BOOLEAN` | `NOT NULL, DEFAULT TRUE` | Account active state |
| `created_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Creation timestamp |
| `updated_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Last update timestamp |

---

### 2.2 Table: `user_quotas` (Phase 8B)
- Manages lifetime or recurring token and cost quotas. `NULL` limits represent unlimited quotas.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | Unique quota record ID |
| `user_id` | `UUID` | `FOREIGN KEY (users.id), UNIQUE, NOT NULL` | Owner user reference |
| `token_limit` | `BIGINT` | `NULLABLE` | Maximum allowed tokens (`NULL` = unlimited) |
| `tokens_used` | `BIGINT` | `NOT NULL, DEFAULT 0` | Cumulative tokens consumed |
| `cost_limit` | `NUMERIC(10, 4)` | `NULLABLE` | Maximum spend limit USD (`NULL` = unlimited) |
| `cost_used` | `NUMERIC(10, 4)` | `NOT NULL, DEFAULT 0.0000` | Cumulative cost consumed USD |
| `reset_at` | `TIMESTAMP WITH TZ` | `NULLABLE` | Scheduled quota reset date |
| `updated_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Last modification timestamp |

---

### 2.3 Table: `usage_records` (Phase 8B)
- Granular per-inference telemetry log linking AI operations back to users and research jobs.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | Telemetry record ID |
| `user_id` | `UUID` | `FOREIGN KEY (users.id), NULLABLE` | Authenticated user ID |
| `job_id` | `UUID` | `FOREIGN KEY (research_jobs.id), NULLABLE`| Associated research job |
| `task_id` | `UUID` | `NULLABLE` | Associated DAG task ID |
| `provider` | `VARCHAR(50)` | `NOT NULL` | Provider name (`ollama`, `gemini`, `openai`) |
| `model` | `VARCHAR(100)` | `NOT NULL` | Exact model name |
| `input_tokens` | `INTEGER` | `NOT NULL, DEFAULT 0` | Prompt token count |
| `output_tokens` | `INTEGER` | `NOT NULL, DEFAULT 0` | Completion token count |
| `total_tokens` | `INTEGER` | `NOT NULL, DEFAULT 0` | Summed token count |
| `estimated_cost`| `NUMERIC(10, 6)` | `NOT NULL, DEFAULT 0.000000` | Computed USD cost |
| `latency_ms` | `FLOAT` | `NOT NULL, DEFAULT 0.0` | Execution latency in milliseconds |
| `created_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Timestamp of inference |

---

### 2.4 Table: `research_jobs`
- Represents top-level research inquiries.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | Research job ID |
| `user_id` | `UUID` | `FOREIGN KEY (users.id), NULLABLE` | Submitting user ID |
| `request_id` | `UUID` | `NOT NULL` | Correlation tracking ID |
| `question` | `TEXT` | `NOT NULL` | User research prompt |
| `objective` | `TEXT` | `NULLABLE` | Planner-decomposed objective |
| `domain` | `VARCHAR(100)` | `NULLABLE` | Detected inquiry domain |
| `scope` | `TEXT` | `NULLABLE` | Research boundary definitions |
| `constraints` | `JSONB / JSON` | `NULLABLE` | Query constraints |
| `expected_output`| `VARCHAR(100)` | `NULLABLE` | Target output format |
| `status` | `VARCHAR(30)` | `NOT NULL, DEFAULT 'pending'` | Job status (`pending`, `running`, `completed`, `failed`) |
| `error_message` | `TEXT` | `NULLABLE` | Failure diagnostic message |
| `started_at` | `TIMESTAMP WITH TZ` | `NULLABLE` | Start execution time |
| `completed_at` | `TIMESTAMP WITH TZ` | `NULLABLE` | Finish execution time |

---

### 2.5 Structured JSON Contracts: Deep Research Engine (Phase 15)

#### `DeepResearchConfig` (Stored within `research_jobs.constraints` or pipeline request)
```json
{
  "max_iterations": 3,
  "confidence_threshold": 0.85,
  "diminishing_returns_threshold": 0.02,
  "max_subtasks_per_iteration": 4,
  "enable_recursive_hypotheses": true
}
```

#### `ResearchIteration` (Stored within `reports.metadata_json.iterations`)
```json
{
  "iteration_index": 1,
  "hypotheses": ["Higher batch sizes reduce communication overhead in federated learning."],
  "scheduled_task_ids": ["uuid-1", "uuid-2"],
  "completed_task_ids": ["uuid-1", "uuid-2"],
  "evidence_count": 14,
  "confidence_score": 0.88,
  "unresolved_gaps": [],
  "gap_queries": [],
  "status": "converged",
  "created_at": "2026-09-12T13:30:00Z"
}
```

---

### 2.6 Table: `research_memories` (Phase 16)
- Represents persistent, cross-session distilled research findings, methodologies, and concepts.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | Unique memory item ID |
| `user_id` | `UUID` | `FOREIGN KEY (users.id), NOT NULL` | Owning authenticated user ID |
| `project_id` | `UUID` | `NULLABLE` | Associated project workspace ID |
| `job_id` | `UUID` | `FOREIGN KEY (research_jobs.id), NULLABLE` | Originating research job ID |
| `memory_type` | `VARCHAR(50)` | `NOT NULL, DEFAULT 'concept'` | Type: `concept`, `finding`, `hypothesis`, `methodology`, `fact` |
| `title` | `VARCHAR(255)` | `NOT NULL` | Short title / conceptual headline |
| `content` | `TEXT` | `NOT NULL` | Markdown-formatted distilled knowledge body |
| `tags` | `JSONB / JSON` | `NOT NULL, DEFAULT '[]'` | Categorization tags for keyword filtering |
| `confidence_score` | `FLOAT` | `NOT NULL, DEFAULT 1.0` | Confidence level [0.0, 1.0] |
| `provenance_json` | `JSONB / JSON` | `NOT NULL, DEFAULT '{}'` | Provenance metadata (`source`, `source_id`, `url`, `chunk_id`) |
| `access_count` | `INTEGER` | `NOT NULL, DEFAULT 0` | Historical recall frequency count |
| `last_accessed_at` | `TIMESTAMP WITH TZ` | `NULLABLE` | Timestamp of most recent recall |
| `created_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Creation timestamp |
| `updated_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Last modification timestamp |

#### Indexes:
- `ix_research_memories_user_id` (`user_id`)
- `ix_research_memories_project_id` (`project_id`)
- `ix_research_memories_memory_type` (`memory_type`)
- `ix_research_memories_title` (`title`)

#### Memory Item Schema (`MemoryItem` / API Contract):
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "project_id": null,
  "job_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "memory_type": "finding",
  "title": "Degradation Rate of PLA in Marine Environments",
  "content": "Polylactic acid (PLA) degrades at less than 1.5% per year in ambient seawater (15-20°C).",
  "tags": ["materials", "marine-biodegradation", "pla"],
  "confidence": 0.94,
  "provenance": {
    "source": "paper",
    "source_id": "doi:10.1016/j.polymdegradstab.2025.109876",
    "url": "https://doi.org/10.1016/j.polymdegradstab.2025.109876"
  },
  "access_count": 3,
  "last_accessed_at": "2026-09-12T14:15:00Z",
  "created_at": "2026-09-12T13:45:00Z",
  "updated_at": "2026-09-12T14:15:00Z"
}
```

---

### 2.7 Table: `knowledge_entities` (Phase 17)
- Represents conceptual nodes, technologies, materials, metrics, datasets, papers, and persons in the persistent Research Knowledge Graph.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | Unique entity node UUID |
| `user_id` | `UUID` | `FOREIGN KEY (users.id), NULLABLE` | Optional owning user ID |
| `project_id` | `UUID` | `NULLABLE` | Optional associated project UUID |
| `name` | `VARCHAR(255)` | `NOT NULL` | Entity name / label |
| `canonical_name` | `VARCHAR(255)` | `NOT NULL` | Normalized lowercase canonical entity key |
| `entity_type` | `VARCHAR(50)` | `NOT NULL, DEFAULT 'CONCEPT'` | Type: `CONCEPT`, `TECHNOLOGY`, `MATERIAL`, `PERSON`, `ORGANIZATION`, `METRIC`, `DATASET`, `PAPER`, `LOCATION`, `OTHER` |
| `description` | `TEXT` | `NULLABLE` | Contextual conceptual description |
| `aliases` | `JSONB / JSON` | `NOT NULL, DEFAULT '[]'` | Synonyms and alias names |
| `properties_json` | `JSONB / JSON` | `NOT NULL, DEFAULT '{}'` | Arbitrary metadata key-values |
| `confidence` | `FLOAT` | `NOT NULL, DEFAULT 1.0` | Confidence rating [0.0, 1.0] |
| `created_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Creation timestamp |
| `updated_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Last update timestamp |

#### Indexes:
- `ix_knowledge_entities_canonical_name` (`canonical_name`)
- `ix_knowledge_entities_entity_type` (`entity_type`)
- `ix_knowledge_entities_user_id` (`user_id`)
- `ix_knowledge_entities_project_id` (`project_id`)

---

### 2.8 Table: `knowledge_relations` (Phase 17)
- Represents directed relational edges connecting knowledge entities in the Graph.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | Unique relation edge UUID |
| `source_id` | `UUID` | `FOREIGN KEY (knowledge_entities.id), NOT NULL` | Source entity node ID |
| `target_id` | `UUID` | `FOREIGN KEY (knowledge_entities.id), NOT NULL` | Target entity node ID |
| `relation_type` | `VARCHAR(100)` | `NOT NULL, DEFAULT 'RELATES_TO'` | Predicate: `AUTHORED_BY`, `USES_MATERIAL`, `CONTRADICTS`, `EVALUATED_ON`, `DEVELOPED_BY`, `CORRELATES_WITH`, `DERIVED_FROM`, `APPLIES_METHODOLOGY`, `EXPOSED_TO`, `HOSTS`, `SECRETES`, `ENHANCES`, `SYNTHESIZED_VIA`, `RELATES_TO` |
| `user_id` | `UUID` | `FOREIGN KEY (users.id), NULLABLE` | Optional owning user ID |
| `project_id` | `UUID` | `NULLABLE` | Optional associated project UUID |
| `job_id` | `UUID` | `FOREIGN KEY (research_jobs.id), NULLABLE` | Associated research job ID |
| `description` | `TEXT` | `NULLABLE` | Relational context / explanation |
| `weight` | `FLOAT` | `NOT NULL, DEFAULT 1.0` | Connection weight / strength |
| `confidence` | `FLOAT` | `NOT NULL, DEFAULT 1.0` | Confidence score [0.0, 1.0] |
| `evidence_id` | `UUID` | `FOREIGN KEY (evidence.id), NULLABLE` | Linked research evidence UUID |
| `properties_json` | `JSONB / JSON` | `NOT NULL, DEFAULT '{}'` | Arbitrary edge metadata |
| `created_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Creation timestamp |

#### Indexes:
- `ix_knowledge_relations_source_id` (`source_id`)
- `ix_knowledge_relations_target_id` (`target_id`)
- `ix_knowledge_relations_relation_type` (`relation_type`)
- `ix_knowledge_relations_job_id` (`job_id`)
- `ix_knowledge_relations_user_id` (`user_id`)
- `ix_knowledge_relations_src_tgt_type` (`source_id`, `target_id`, `relation_type`)

---

### 2.9 Table: `workspaces` (Phase 18)
- Multi-tenant workspace grouping users, projects, and research artifacts.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | Unique workspace UUID |
| `name` | `VARCHAR(255)` | `NOT NULL` | Workspace name |
| `slug` | `VARCHAR(255)` | `UNIQUE, NOT NULL` | URL-safe slug |
| `description` | `TEXT` | `NULLABLE` | Workspace description |
| `owner_id` | `UUID` | `FOREIGN KEY (users.id), NOT NULL` | Owning user UUID |
| `is_personal` | `BOOLEAN` | `NOT NULL, DEFAULT FALSE` | Flag for personal workspace |
| `settings_json` | `JSONB / JSON` | `NOT NULL, DEFAULT '{}'` | Custom workspace settings |
| `created_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Creation timestamp |
| `updated_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Last update timestamp |

---

### 2.10 Table: `workspace_members` (Phase 18)
- Join table linking users to workspaces with RBAC roles.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | Unique membership UUID |
| `workspace_id` | `UUID` | `FOREIGN KEY (workspaces.id), NOT NULL` | Associated workspace |
| `user_id` | `UUID` | `FOREIGN KEY (users.id), NOT NULL` | Associated user |
| `role` | `VARCHAR(50)` | `NOT NULL, DEFAULT 'member'` | Role: `owner`, `admin`, `researcher`, `member`, `viewer` |
| `created_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Creation timestamp |
| `updated_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Last update timestamp |

---

### 2.11 Table: `projects` (Phase 18)
- Project workspace container scoping research jobs, documents, memories, and knowledge graphs.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | Unique project UUID |
| `workspace_id` | `UUID` | `FOREIGN KEY (workspaces.id), NOT NULL` | Owning workspace UUID |
| `name` | `VARCHAR(255)` | `NOT NULL` | Project name |
| `slug` | `VARCHAR(255)` | `NOT NULL` | Project slug (unique within workspace) |
| `description` | `TEXT` | `NULLABLE` | Project goals and description |
| `created_by` | `UUID` | `FOREIGN KEY (users.id), NULLABLE` | Creator user UUID |
| `status` | `VARCHAR(50)` | `NOT NULL, DEFAULT 'active'` | Status: `active`, `archived` |
| `settings_json` | `JSONB / JSON` | `NOT NULL, DEFAULT '{}'` | Project configuration |
| `created_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Creation timestamp |
| `updated_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Last update timestamp |

---

### 2.12 Table: `workspace_invites` (Phase 19)
- Managed via `packages/database/src/database/models/collaboration.py`.
- Stores pending and accepted email invitations to workspaces.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID / CHAR(36)` | `PRIMARY KEY` | Unique invitation ID |
| `workspace_id` | `UUID / CHAR(36)` | `NOT NULL, FK -> workspaces.id CASCADE, INDEX` | Target workspace |
| `email` | `VARCHAR(255)` | `NOT NULL, INDEX` | Recipient email address |
| `role` | `VARCHAR(50)` | `NOT NULL, DEFAULT 'researcher'` | Assigned role (`admin`, `researcher`, `analyst`, `reviewer`, `viewer`) |
| `token` | `VARCHAR(128)` | `UNIQUE, NOT NULL, INDEX` | URL-safe cryptographic redemption token |
| `invited_by` | `UUID / CHAR(36)` | `NULLABLE, FK -> users.id SET NULL` | Inviting user ID |
| `is_accepted` | `BOOLEAN` | `NOT NULL, DEFAULT FALSE, INDEX` | Acceptance flag |
| `expires_at` | `TIMESTAMP WITH TZ` | `NOT NULL` | Expiration timestamp (default +7 days) |
| `created_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Creation timestamp |

---

### 2.13 Table: `report_annotations` (Phase 19)
- Stores collaborative inline review comments on generated research reports.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID / CHAR(36)` | `PRIMARY KEY` | Unique annotation ID |
| `report_id` | `UUID / CHAR(36)` | `NOT NULL, FK -> reports.id CASCADE, INDEX` | Research report ID |
| `user_id` | `UUID / CHAR(36)` | `NOT NULL, FK -> users.id CASCADE, INDEX` | Author user ID |
| `section_index` | `INTEGER` | `NULLABLE` | Index of findings section or paragraph |
| `selected_text` | `TEXT` | `NULLABLE` | Highlighted/quoted text snippet |
| `comment_text` | `TEXT` | `NOT NULL` | Review note or recommendation |
| `status` | `VARCHAR(50)` | `NOT NULL, DEFAULT 'open', INDEX` | Status: `open`, `resolved` |
| `resolved_by` | `UUID / CHAR(36)` | `NULLABLE, FK -> users.id SET NULL` | User who resolved the comment |
| `resolved_at` | `TIMESTAMP WITH TZ` | `NULLABLE` | Resolution timestamp |
| `created_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Creation timestamp |
| `updated_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Last modification timestamp |

---

### 2.14 Table: `workspace_activities` (Phase 19)
- Immutable chronological audit activity feed for workspaces and projects.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID / CHAR(36)` | `PRIMARY KEY` | Unique activity event ID |
| `workspace_id` | `UUID / CHAR(36)` | `NOT NULL, FK -> workspaces.id CASCADE, INDEX` | Target workspace ID |
| `project_id` | `UUID / CHAR(36)` | `NULLABLE, FK -> projects.id SET NULL, INDEX` | Associated project ID |
| `user_id` | `UUID / CHAR(36)` | `NULLABLE, FK -> users.id SET NULL, INDEX` | Triggering user ID |
| `action` | `VARCHAR(100)` | `NOT NULL, INDEX` | Action identifier (`member_invited`, `member_joined`, `job_created`, `doc_uploaded`, etc.) |
| `entity_id` | `UUID / CHAR(36)` | `NULLABLE` | Target entity ID |
| `details_json` | `JSONB / JSON` | `NOT NULL, DEFAULT '{}'` | Arbitrary structured event metadata |
| `created_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW(), INDEX` | Event timestamp |

---

## 3. Database Cross-Compatibility Strategy

To ensure seamless production deployment on PostgreSQL 16 while supporting fast, zero-dependency in-memory testing with SQLite, all model definitions use SQLAlchemy dialect-agnostic variants:

```python
from sqlalchemy import JSON, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.types import TypeDecorator, CHAR
import uuid

# Dialect-safe UUID Type
class GUID(TypeDecorator):
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID())
        return dialect.type_descriptor(CHAR(36))

# Dialect-safe JSON Type
JSONType = JSON().with_variant(JSONB, "postgresql")
```

---

---

## 4. Model Ecosystem Optimization API Contracts (Phase 20)

### 4.1 GET `/api/v1/models/profiles`
Returns all preset routing optimization profiles and their constituent weight vectors.

**Response (200 OK):**
```json
{
  "balanced": {
    "name": "Balanced Ecosystem",
    "profile_type": "balanced",
    "quality_weight": 0.35,
    "speed_weight": 0.25,
    "cost_weight": 0.30,
    "locality_weight": 0.10,
    "prefer_local": true,
    "description": "Even trade-off between reasoning quality, execution speed, and token cost."
  },
  "cost_minimized": {
    "name": "Cost Minimized",
    "profile_type": "cost_minimized",
    "quality_weight": 0.20,
    "speed_weight": 0.15,
    "cost_weight": 0.55,
    "locality_weight": 0.10,
    "prefer_local": true,
    "description": "Prioritizes free tiers and low-cost models to maximize budget efficiency."
  },
  "speed_maximized": {
    "name": "Speed Maximized",
    "profile_type": "speed_maximized",
    "quality_weight": 0.20,
    "speed_weight": 0.55,
    "cost_weight": 0.10,
    "locality_weight": 0.15,
    "prefer_local": true,
    "description": "Prioritizes fast inference, lightweight models, and local low-latency engines."
  },
  "quality_maximized": {
    "name": "Quality & Reasoning Maximized",
    "profile_type": "quality_maximized",
    "quality_weight": 0.75,
    "speed_weight": 0.10,
    "cost_weight": 0.10,
    "locality_weight": 0.05,
    "prefer_local": false,
    "description": "Selects the highest capability frontier models for deep reasoning and synthesis."
  }
}
```

### 4.2 POST `/api/v1/models/optimize`
Simulates candidate model evaluation, calculates Pareto-optimal frontier, and returns ranked utility scores.

**Request Body:**
```json
{
  "task": "long_form_research",
  "profile": "balanced",
  "required_capabilities": ["reasoning", "summarization"]
}
```

**Response (200 OK):**
```json
{
  "selected_model_id": "gemini-2.5-pro",
  "selected_provider": "gemini",
  "profile_used": {
    "name": "Balanced Ecosystem",
    "profile_type": "balanced",
    "quality_weight": 0.35,
    "speed_weight": 0.25,
    "cost_weight": 0.30,
    "locality_weight": 0.10
  },
  "ranked_candidates": [
    {
      "model_id": "gemini-2.5-pro",
      "provider_name": "gemini",
      "total_score": 0.825,
      "quality_score": 0.95,
      "speed_score": 0.70,
      "cost_score": 0.65,
      "locality_score": 0.30,
      "is_pareto_optimal": true,
      "rank": 1,
      "tier": "paid",
      "is_local": false,
      "estimated_cost_per_1k": 0.003125,
      "rationale": "Pareto-optimal trade-off, Specialized for 'long_form_research', High reasoning score"
    }
  ],
  "pareto_frontier": ["gemini-2.5-pro", "ollama-llama3.3:70b"],
  "tradeoff_analysis": "Selected 'gemini-2.5-pro' via Balanced Ecosystem (Score: 0.825). Model is on the non-dominated Pareto frontier."
}
```

---

## 5. Model Evaluation System Schemas & REST APIs (Phase 21)

### 5.1 Table: `model_evaluations`
Tracks top-level offline benchmark runs evaluating model performance against golden datasets.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | Unique evaluation run ID |
| `model_id` | `VARCHAR(100)` | `NOT NULL, INDEX` | Evaluated model ID |
| `provider_name` | `VARCHAR(50)` | `NOT NULL` | AI Provider name |
| `benchmark_name` | `VARCHAR(100)` | `NOT NULL, DEFAULT 'research_core_eval_v1'` | Benchmark dataset identifier |
| `total_samples` | `INTEGER` | `NOT NULL, DEFAULT 0` | Total test cases in run |
| `passed_samples` | `INTEGER` | `NOT NULL, DEFAULT 0` | Test cases meeting pass threshold |
| `pass_rate` | `FLOAT` | `NOT NULL, DEFAULT 0.0` | Proportion of passed samples [0.0 - 1.0] |
| `overall_score` | `FLOAT` | `NOT NULL, DEFAULT 0.0` | Weighted composite score [0.0 - 1.0] |
| `mean_accuracy` | `FLOAT` | `NOT NULL, DEFAULT 0.0` | Mean factual keyword accuracy |
| `mean_reasoning` | `FLOAT` | `NOT NULL, DEFAULT 0.0` | Mean multi-step reasoning score |
| `mean_faithfulness`| `FLOAT` | `NOT NULL, DEFAULT 0.0` | Mean retrieval context faithfulness |
| `mean_citation_precision` | `FLOAT` | `NOT NULL, DEFAULT 0.0` | Mean citation match precision |
| `mean_latency_ms`| `FLOAT` | `NOT NULL, DEFAULT 0.0` | Average response latency (ms) |
| `total_cost_usd` | `NUMERIC(10, 6)` | `NOT NULL, DEFAULT 0.000000` | Cumulative execution cost in USD |
| `category_scores`| `JSONB / JSON` | `NOT NULL, DEFAULT '{}'` | Category-level aggregated score map |
| `triggered_by` | `UUID` | `FOREIGN KEY (users.id), NULLABLE` | Triggering user identifier |
| `created_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Run execution timestamp |

---

### 5.2 Table: `model_benchmark_results`
Individual sample test case outputs and diagnostic breakdowns for an evaluation run.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | Test case result ID |
| `evaluation_id` | `UUID` | `FOREIGN KEY (model_evaluations.id ON DELETE CASCADE), NOT NULL` | Parent evaluation run |
| `sample_id` | `VARCHAR(100)` | `NOT NULL` | Benchmark sample case ID |
| `category` | `VARCHAR(50)` | `NOT NULL` | Category (reasoning, factual, etc.) |
| `prompt` | `TEXT` | `NOT NULL` | Input prompt presented to model |
| `response_text` | `TEXT` | `NOT NULL` | Generated model completion |
| `passed` | `BOOLEAN` | `NOT NULL, DEFAULT TRUE` | Sample passed indicator |
| `score` | `FLOAT` | `NOT NULL, DEFAULT 0.0` | Sample composite score |
| `metrics` | `JSONB / JSON` | `NOT NULL, DEFAULT '{}'` | Dimensional metrics breakdown |
| `latency_ms` | `INTEGER` | `NOT NULL, DEFAULT 0` | Sample execution latency |
| `prompt_tokens` | `INTEGER` | `NOT NULL, DEFAULT 0` | Prompt token count |
| `completion_tokens` | `INTEGER` | `NOT NULL, DEFAULT 0` | Output token count |
| `cost_usd` | `NUMERIC(10, 6)` | `NOT NULL, DEFAULT 0.000000` | Sample cost in USD |
| `error` | `TEXT` | `NULLABLE` | Error message if failed |
| `created_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Creation timestamp |

---

### 5.3 REST Endpoints (Phase 21)

#### `POST /api/v1/models/evaluate`
Triggers an automated benchmark evaluation run across golden test cases.

**Request:**
```json
{
  "model_id": "gemini-2.0-flash",
  "benchmark_name": "research_core_eval_v1"
}
```

#### `GET /api/v1/models/leaderboard`
Returns an aggregated competitive model leaderboard ranked by overall score with Pareto frontier flags.

**Response:**
```json
[
  {
    "rank": 1,
    "model_id": "gemini-2.0-flash",
    "provider_name": "gemini",
    "overall_score": 0.892,
    "factual_accuracy": 0.940,
    "reasoning_depth": 0.885,
    "retrieval_faithfulness": 0.920,
    "citation_precision": 0.850,
    "mean_latency_ms": 320.0,
    "cost_per_1k_usd": 0.00015,
    "tier": "paid",
    "is_local": false,
    "is_pareto_optimal": true,
    "last_evaluated": "2026-09-13T10:00:00Z"
  }
]
```

---

## 6. Agent Evaluation & Observability Schemas & REST APIs (Phase 22)

### 6.1 Table: `agent_evaluations`
Tracks autonomous multi-agent execution scorecards assessing reasoning precision, tool accuracy, evidence coverage, and hallucination rates.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | Unique evaluation scorecard ID |
| `agent_name` | `VARCHAR(100)` | `NOT NULL, INDEX` | Agent type/name (e.g. `ResearchPipeline`, `WebResearchAgent`) |
| `job_id` | `UUID` | `FOREIGN KEY (research_jobs.id ON DELETE SET NULL), NULLABLE` | Optional associated research job |
| `total_steps` | `INTEGER` | `NOT NULL, DEFAULT 0` | Total sequential steps executed |
| `successful_steps` | `INTEGER` | `NOT NULL, DEFAULT 0` | Steps succeeding without error |
| `failed_steps` | `INTEGER` | `NOT NULL, DEFAULT 0` | Steps encountering errors or crashes |
| `plan_precision` | `FLOAT` | `NOT NULL, DEFAULT 0.0` | Plan DAG relevance and diversity [0.0 - 1.0] |
| `tool_accuracy` | `FLOAT` | `NOT NULL, DEFAULT 0.0` | Proportion of successful tool invocations |
| `evidence_coverage` | `FLOAT` | `NOT NULL, DEFAULT 0.0` | Proportion of claims grounded in evidence |
| `hallucination_rate` | `FLOAT` | `NOT NULL, DEFAULT 0.0` | Ratio of ungrounded sentences [0.0 - 1.0] |
| `synthesis_fidelity` | `FLOAT` | `NOT NULL, DEFAULT 0.0` | Report faithfulness (1 - hallucination_rate) |
| `overall_score` | `FLOAT` | `NOT NULL, DEFAULT 0.0` | Composite weighted agent execution score |
| `execution_time_ms` | `INTEGER` | `NOT NULL, DEFAULT 0` | Total agent execution runtime in ms |
| `total_tokens` | `INTEGER` | `NOT NULL, DEFAULT 0` | Total tokens consumed by agent steps |
| `estimated_cost_usd` | `NUMERIC(10, 6)` | `NOT NULL, DEFAULT 0.000000` | Estimated USD inference cost |
| `findings_audit` | `JSONB / JSON` | `NOT NULL, DEFAULT '{}'` | Breakdown of evaluated claims and sources |
| `evaluated_by` | `UUID` | `FOREIGN KEY (users.id ON DELETE SET NULL), NULLABLE` | Triggering user ID |
| `created_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Scorecard creation timestamp |

---

### 6.2 Table: `agent_step_metrics`
Individual step telemetry records for sequential agent actions.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | Step metric ID |
| `evaluation_id` | `UUID` | `FOREIGN KEY (agent_evaluations.id ON DELETE CASCADE), NOT NULL` | Parent evaluation scorecard |
| `step_index` | `INTEGER` | `NOT NULL` | Sequence order index |
| `agent_type` | `VARCHAR(100)` | `NOT NULL` | Agent identifier for this step |
| `action_type` | `VARCHAR(50)` | `NOT NULL` | Action category (`plan`, `tool_execution`, `synthesis`) |
| `tool_name` | `VARCHAR(100)` | `NULLABLE` | Invoked tool name (if applicable) |
| `tool_args` | `JSONB / JSON` | `NOT NULL, DEFAULT '{}'` | Tool input arguments |
| `tool_output_length` | `INTEGER` | `NOT NULL, DEFAULT 0` | Character length of tool return |
| `success` | `BOOLEAN` | `NOT NULL, DEFAULT TRUE` | Execution success status |
| `error_message` | `TEXT` | `NULLABLE` | Error diagnostic if step failed |
| `latency_ms` | `INTEGER` | `NOT NULL, DEFAULT 0` | Step execution duration in ms |
| `tokens_consumed` | `INTEGER` | `NOT NULL, DEFAULT 0` | Tokens consumed in step |
| `created_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Step record timestamp |

---

### 6.3 REST Endpoints (Phase 22)

#### `POST /api/v1/agents/evaluate`
Calculates and persists an agent evaluation scorecard with step telemetry.

**Request:**
```json
{
  "agent_name": "WebResearchAgent",
  "research_objective": "Transformer scaling laws exploration",
  "plan_tasks": [{"title": "Search transformer papers"}],
  "step_telemetry": [
    {
      "step_index": 1,
      "agent_type": "WebResearchAgent",
      "action_type": "tool_execution",
      "tool_name": "web_search",
      "tool_args": {"query": "transformer scaling laws"},
      "tool_output_length": 150,
      "success": true,
      "latency_ms": 110,
      "tokens_consumed": 50
    }
  ],
  "evidence_items": [{"content": "Transformer models scale with compute."}],
  "report_text": "Transformer models scale with compute.",
  "claims": ["Transformer models scale with compute."],
  "execution_time_ms": 360,
  "total_tokens": 200,
  "cost_usd": 0.00004
}
```

#### `GET /api/v1/agents/evaluations`
Lists historical agent evaluation scorecards with filtering by `agent_name` and `job_id`.

#### `GET /api/v1/agents/evaluations/{id}`
Retrieves detailed scorecard and full sequential step telemetry history.

#### `GET /api/v1/agents/metrics/summary`
Returns system-wide aggregated agent metrics (mean score, plan precision, tool accuracy, evidence coverage, hallucination rate, total tokens, total cost).

---

## 7. Enterprise Security, KMS Secret Vault & Audit Trail Schemas (Phase 23)

### 7.1 Table: `security_audit_logs`
Immutable, tamper-evident audit logs with cryptographic SHA-256 hash chaining forming a verifiable Merkle sequence:
$$\text{CurrentHash} = \text{SHA256}(\text{PreviousHash} \parallel \text{Timestamp} \parallel \text{EventType} \parallel \text{ActorId} \parallel \text{ResourceId} \parallel \text{Details})$$

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | Unique audit log ID |
| `event_type` | `VARCHAR(100)` | `NOT NULL, INDEX` | Event category (`user.login`, `secret.access`, `gdpr.purge`) |
| `severity` | `VARCHAR(30)` | `NOT NULL, DEFAULT 'INFO'` | Event severity (`INFO`, `WARNING`, `CRITICAL`) |
| `actor_id` | `UUID` | `FOREIGN KEY (users.id ON DELETE SET NULL), NULLABLE` | Triggering actor ID |
| `workspace_id` | `UUID` | `FOREIGN KEY (workspaces.id ON DELETE SET NULL), NULLABLE` | Associated tenant workspace |
| `resource_type` | `VARCHAR(100)` | `NULLABLE` | Targeted resource entity type |
| `resource_id` | `VARCHAR(255)` | `NULLABLE` | Targeted resource ID |
| `action` | `VARCHAR(100)` | `NOT NULL` | Specific action taken |
| `details` | `JSONB / JSON` | `NOT NULL, DEFAULT '{}'` | Serialized contextual payload |
| `ip_address` | `VARCHAR(45)` | `NULLABLE` | Client IPv4 / IPv6 address |
| `user_agent` | `TEXT` | `NULLABLE` | Client browser / CLI user agent string |
| `previous_hash` | `VARCHAR(64)` | `NOT NULL, INDEX` | SHA-256 hash of previous record (or Genesis) |
| `current_hash` | `VARCHAR(64)` | `NOT NULL, INDEX` | SHA-256 hash chaining record data |
| `created_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW(), INDEX` | Immutable timestamp |

---

### 7.2 Table: `encrypted_secrets`
KMS Two-Tier Envelope Encrypted Secrets Vault (AES-256-GCM DEK/KEK architecture).

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | Unique secret record ID |
| `name` | `VARCHAR(100)` | `NOT NULL, INDEX` | Human-readable secret label |
| `secret_type` | `VARCHAR(50)` | `NOT NULL` | Secret classification (`api_key`, `oauth_token`, `database_uri`) |
| `provider` | `VARCHAR(50)` | `NOT NULL, INDEX` | Target provider (`gemini`, `openai`, `anthropic`, `custom`) |
| `key_version` | `VARCHAR(50)` | `NOT NULL, DEFAULT 'v1-aes256gcm'` | KMS key version identifier |
| `encrypted_payload`| `TEXT` | `NOT NULL` | Base64-encoded AES-256-GCM ciphertext payload |
| `encrypted_dek` | `TEXT` | `NOT NULL` | Base64-encoded DEK wrapped by KEK |
| `masked_preview` | `VARCHAR(50)` | `NOT NULL` | Masked identifier string for display (e.g. `AIz...8877`) |
| `workspace_id` | `UUID` | `FOREIGN KEY (workspaces.id ON DELETE CASCADE), NULLABLE` | Scoped workspace |
| `created_by` | `UUID` | `FOREIGN KEY (users.id ON DELETE SET NULL), NULLABLE` | Owning user ID |
| `is_revoked` | `BOOLEAN` | `NOT NULL, DEFAULT FALSE` | Vault revocation flag |
| `created_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Creation timestamp |
| `updated_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Last update timestamp |

---

### 7.3 Table: `security_policies`
Workspace security constraints, retention lifecycles, and compliance rules.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | Unique policy ID |
| `workspace_id` | `UUID` | `FOREIGN KEY (workspaces.id ON DELETE CASCADE), UNIQUE` | Scoped workspace ID |
| `retention_days` | `INTEGER` | `NOT NULL, DEFAULT 365` | Data retention lifespan in days |
| `enforce_mfa` | `BOOLEAN` | `NOT NULL, DEFAULT FALSE` | Multi-Factor Authentication requirement |
| `ip_whitelist` | `JSONB / JSON` | `NOT NULL, DEFAULT '{"allowed_cidrs": []}'` | Allowed CIDR IP whitelist |
| `allowed_providers` | `JSONB / JSON` | `NOT NULL, DEFAULT '{"providers": ["gemini", "ollama", "openai"]}'` | Whitelisted LLM providers |
| `gdpr_anonymize_on_delete` | `BOOLEAN` | `NOT NULL, DEFAULT TRUE` | Automated anonymization on deletion |
| `data_classification` | `VARCHAR(50)` | `NOT NULL, DEFAULT 'CONFIDENTIAL'` | Classification (`PUBLIC`, `INTERNAL`, `CONFIDENTIAL`, `RESTRICTED`) |
| `updated_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Last modification timestamp |

---

### 7.4 REST Endpoints (Phase 23)

- `POST /api/v1/security/audit-logs`: Record an immutable, hash-chained security audit log entry.
- `GET /api/v1/security/audit-logs`: Query historical security audit logs with filtering.
- `GET /api/v1/security/audit-logs/verify`: Cryptographically verify SHA-256 hash chain integrity of audit logs.
- `POST /api/v1/security/secrets`: Store encrypted credentials into KMS envelope vault.
- `GET /api/v1/security/secrets`: List vaulted secrets metadata with masked previews.
- `PATCH /api/v1/security/secrets/{id}/revoke`: Revoke credentials in vault.
- `DELETE /api/v1/security/secrets/{id}`: Permanently delete credentials from vault.
- `GET /api/v1/security/policy`: Retrieve workspace security policy and retention rules.
- `PATCH /api/v1/security/policy`: Update workspace security policy, MFA, and CIDR whitelist.
- `POST /api/v1/security/gdpr/purge`: Execute GDPR Right-to-be-Forgotten cascade data purge.
- `GET /api/v1/security/compliance/status`: Retrieve SOC 2 and GDPR compliance scorecard.

---

## 8. Production Infrastructure Schema & Contracts (Phase 24)

### 8.1 Table: `worker_nodes`
Tracks distributed worker node health, active tasks, heartbeat leases, and node capabilities.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `node_id` | `VARCHAR(100)` | `PRIMARY KEY` | Unique worker instance identifier |
| `hostname` | `VARCHAR(255)` | `NOT NULL` | Node network host name |
| `status` | `VARCHAR(50)` | `NOT NULL, DEFAULT 'ready', INDEX` | Lifecycle state (`ready`, `busy`, `draining`, `offline`) |
| `current_task_id` | `VARCHAR(100)` | `NULLABLE, INDEX` | Currently assigned task ID |
| `concurrency_limit` | `INTEGER` | `NOT NULL, DEFAULT 4` | Maximum parallel execution threads |
| `active_task_count` | `INTEGER` | `NOT NULL, DEFAULT 0` | Current active execution count |
| `capabilities` | `JSONB / JSON` | `NOT NULL, DEFAULT '[]'` | Worker specializations (`["web_search", "multimodal", "pdf_parsing"]`) |
| `metrics` | `JSONB / JSON` | `NOT NULL, DEFAULT '{}'` | System load (CPU, RAM, task completed count) |
| `last_heartbeat` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW(), INDEX` | Last heartbeat pulse timestamp |
| `started_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Node boot timestamp |
| `updated_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Last status update timestamp |

---

### 8.2 Table: `storage_objects`
Metadata repository for unified object blob storage across Local, MinIO, and AWS S3 backends.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `object_id` | `VARCHAR(100)` | `PRIMARY KEY` | Unique blob identifier |
| `bucket_name` | `VARCHAR(100)` | `NOT NULL, INDEX` | Target storage bucket / namespace |
| `object_key` | `VARCHAR(500)` | `NOT NULL, INDEX` | Path / key inside bucket |
| `content_type` | `VARCHAR(100)` | `NOT NULL, DEFAULT 'application/octet-stream'` | MIME type |
| `size_bytes` | `BIGINT` | `NOT NULL, DEFAULT 0` | File size in bytes |
| `etag` | `VARCHAR(100)` | `NULLABLE` | S3 / MinIO ETag or MD5 digest |
| `storage_class` | `VARCHAR(50)` | `NOT NULL, DEFAULT 'STANDARD'` | Storage tier (`STANDARD`, `INFREQUENT_ACCESS`, `ARCHIVE`) |
| `backend_type` | `VARCHAR(50)` | `NOT NULL, DEFAULT 'local'` | Storage driver (`s3`, `minio`, `local`) |
| `metadata_json` | `JSONB / JSON` | `NOT NULL, DEFAULT '{}'` | User and system object metadata |
| `uploaded_by` | `UUID` | `FOREIGN KEY (users.id ON DELETE SET NULL), NULLABLE` | Uploading user ID |
| `workspace_id` | `UUID` | `FOREIGN KEY (workspaces.id ON DELETE SET NULL), NULLABLE` | Scoped tenant workspace ID |
| `created_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW(), INDEX` | Object creation timestamp |
| `updated_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Last metadata update timestamp |

---

### 8.3 REST Endpoints (Phase 24)

- `GET /api/v1/system/workers`: List registered worker nodes in the cluster with heartbeat telemetry.
- `POST /api/v1/system/workers/heartbeat`: Worker pulse endpoint registering node load, CPU, RAM, and active tasks.
- `GET /api/v1/system/queue/status`: Query distributed queue length, priority distributions, and latency metrics.
- `POST /api/v1/system/queue/tasks`: Enqueue research tasks with priority (`CRITICAL`, `HIGH`, `DEFAULT`, `LOW`).
- `GET /api/v1/system/storage/objects`: Query stored object blobs with workspace filtering and MIME search.
- `POST /api/v1/system/storage/presigned-url`: Generate presigned upload/download URLs for S3/MinIO blobs.
- `GET /api/v1/system/storage/usage`: Compute aggregate blob storage utilization, bucket byte totals, and object counts.

---

## 9. Developer Platform & Public API Schema (Phase 25)

### 9.1 Table: `api_keys`
Cryptographically secure hashed API key storage with prefix indexing, granular permission scopes, and rate limiting tier attributes.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | Unique API key record ID |
| `user_id` | `UUID` | `FOREIGN KEY (users.id ON DELETE CASCADE), NOT NULL, INDEX` | Owner user reference |
| `workspace_id` | `UUID` | `FOREIGN KEY (workspaces.id ON DELETE CASCADE), NULLABLE, INDEX` | Associated workspace ID |
| `name` | `VARCHAR(100)` | `NOT NULL` | Human-readable key label |
| `key_prefix` | `VARCHAR(20)` | `NOT NULL, INDEX` | Plaintext prefix (`amrp_live_...`) for indexing |
| `key_hash` | `VARCHAR(255)` | `NOT NULL, UNIQUE, INDEX` | SHA-256 cryptographic digest of secret key |
| `scopes` | `JSONB / JSON` | `NOT NULL, DEFAULT '["research:read", "research:write", "documents:read", "documents:write"]'` | Granular permission scopes |
| `rate_limit_tier` | `VARCHAR(50)` | `NOT NULL, DEFAULT 'free'` | Rate limit tier (`free`, `pro`, `enterprise`) |
| `rate_limit_rpm` | `INTEGER` | `NOT NULL, DEFAULT 60` | Requests allowed per minute window |
| `is_active` | `BOOLEAN` | `NOT NULL, DEFAULT TRUE` | Active lifecycle status |
| `expires_at` | `TIMESTAMP WITH TZ` | `NULLABLE` | Key expiration date (`NULL` = no expiration) |
| `last_used_at` | `TIMESTAMP WITH TZ` | `NULLABLE` | Last API request timestamp |
| `created_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Creation timestamp |
| `updated_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Last update timestamp |

---

### 9.2 REST Endpoints (Phase 25)

- `GET /api/v1/developer/keys`: List developer API keys for authenticated user with masked preview and usage stats.
- `POST /api/v1/developer/keys`: Generate a new API key; returns full plaintext secret key once (`amrp_live_<48_hex>`) and stores SHA-256 hash.
- `GET /api/v1/developer/keys/{id}`: Retrieve metadata for a specific API key.
- `PATCH /api/v1/developer/keys/{id}/revoke`: Immediately deactivate an API key.
- `DELETE /api/v1/developer/keys/{id}`: Permanently delete an API key record.
- `POST /api/v1/developer/research`: Public API endpoint for enqueuing research inquiries via `X-API-Key` authentication.
- `GET /api/v1/developer/research/{id}`: Public API endpoint for polling research progress and fetching finished reports.
- `POST /api/v1/developer/documents`: Public API endpoint for programmatic document and text ingestion.
- `GET /api/v1/developer/usage`: Public API endpoint for querying developer token and request usage statistics.

---

## 10. Research Automation Schema & REST Endpoints (Phase 26)

### 10.1 Table: `scheduled_research`
Automated scheduled research sweeps with cron or interval triggers, topic definitions, source filters, and novelty thresholds.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | Unique schedule record ID |
| `user_id` | `UUID` | `FOREIGN KEY (users.id ON DELETE CASCADE), NOT NULL, INDEX` | Owning user reference |
| `workspace_id` | `UUID` | `FOREIGN KEY (workspaces.id ON DELETE CASCADE), NULLABLE, INDEX` | Scoped workspace ID |
| `project_id` | `UUID` | `FOREIGN KEY (projects.id ON DELETE SET NULL), NULLABLE, INDEX` | Scoped project ID |
| `title` | `VARCHAR(255)` | `NOT NULL` | Human-readable schedule title |
| `query` | `TEXT` | `NOT NULL` | Research query / topic prompt |
| `cron_expression` | `VARCHAR(100)` | `NULLABLE` | Standard 5-field cron expression (e.g. `0 9 * * 1`) |
| `interval_seconds` | `INTEGER` | `NULLABLE` | Frequency interval in seconds (e.g. `86400`) |
| `is_active` | `BOOLEAN` | `NOT NULL, DEFAULT TRUE, INDEX` | Active polling status |
| `novelty_threshold` | `FLOAT` | `NOT NULL, DEFAULT 0.3` | Score threshold $\in [0, 1]$ triggering alerts |
| `source_filters` | `JSONB / JSON` | `NOT NULL, DEFAULT '["web", "arxiv", "documents"]'` | Sources to query on each sweep |
| `routing_profile` | `VARCHAR(50)` | `NOT NULL, DEFAULT 'balanced'` | Model optimization profile used |
| `alert_channels` | `JSONB / JSON` | `NOT NULL, DEFAULT '["in_app"]'` | Alert destinations (`in_app`, `email`, `webhook`) |
| `webhook_url` | `VARCHAR(500)` | `NULLABLE` | Target URL for automated webhook alerts |
| `last_run_at` | `TIMESTAMP WITH TZ` | `NULLABLE` | Last sweep execution timestamp |
| `next_run_at` | `TIMESTAMP WITH TZ` | `NULLABLE, INDEX` | Next scheduled sweep timestamp |
| `sweep_count` | `INTEGER` | `NOT NULL, DEFAULT 0` | Total sweeps completed |
| `created_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Schedule creation timestamp |
| `updated_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Last update timestamp |

---

### 10.2 Table: `research_sweep_results`
Historical record of completed automated research sweeps with claim diffs, novelty metrics, and findings.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | Unique sweep result ID |
| `schedule_id` | `UUID` | `FOREIGN KEY (scheduled_research.id ON DELETE CASCADE), NOT NULL, INDEX` | Parent schedule ID |
| `job_id` | `VARCHAR(100)` | `NULLABLE, INDEX` | Associated research job ID |
| `findings_summary` | `TEXT` | `NOT NULL` | Synthesized findings from this sweep |
| `novel_claims` | `JSONB / JSON` | `NOT NULL, DEFAULT '[]'` | Newly discovered facts/claims not in prior sweeps |
| `contradictory_claims`| `JSONB / JSON` | `NOT NULL, DEFAULT '[]'` | Claims conflicting with previous knowledge |
| `sources_crawled` | `JSONB / JSON` | `NOT NULL, DEFAULT '[]'` | List of URLs and document IDs retrieved |
| `novelty_score` | `FLOAT` | `NOT NULL, DEFAULT 0.0` | Computed novelty score $\in [0, 1]$ |
| `metrics` | `JSONB / JSON` | `NOT NULL, DEFAULT '{}'` | Sweep duration, token counts, and cost metrics |
| `executed_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW(), INDEX` | Sweep execution timestamp |

---

### 10.3 Table: `automation_alerts`
Dispatched change detection and novelty alerts for user review.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | Unique alert ID |
| `schedule_id` | `UUID` | `FOREIGN KEY (scheduled_research.id ON DELETE CASCADE), NOT NULL, INDEX` | Source schedule ID |
| `sweep_result_id` | `UUID` | `FOREIGN KEY (research_sweep_results.id ON DELETE CASCADE), NOT NULL, INDEX` | Associated sweep result ID |
| `user_id` | `UUID` | `FOREIGN KEY (users.id ON DELETE CASCADE), NOT NULL, INDEX` | Recipient user ID |
| `alert_type` | `VARCHAR(50)` | `NOT NULL, INDEX` | Type (`novel_finding`, `contradiction`, `schedule_error`) |
| `title` | `VARCHAR(255)` | `NOT NULL` | Alert notification title |
| `summary` | `TEXT` | `NOT NULL` | Concise explanation of new finding or change |
| `novelty_score` | `FLOAT` | `NOT NULL, DEFAULT 0.0` | Novelty intensity score |
| `channel` | `VARCHAR(50)` | `NOT NULL, DEFAULT 'in_app'` | Dispatch medium (`in_app`, `email`, `webhook`) |
| `is_read` | `BOOLEAN` | `NOT NULL, DEFAULT FALSE, INDEX` | In-app read status |
| `is_acknowledged` | `BOOLEAN` | `NOT NULL, DEFAULT FALSE, INDEX` | User acknowledgment flag |
| `created_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW(), INDEX` | Alert dispatch timestamp |

---

### 10.4 REST Endpoints (Phase 26)

- `POST /api/v1/automation/schedules`: Create a recurring research schedule with cron/interval timing, novelty threshold, and alert channels.
- `GET /api/v1/automation/schedules`: List research schedules for the authenticated user or workspace.
- `GET /api/v1/automation/schedules/{id}`: Retrieve full details for a scheduled research topic.
- `PATCH /api/v1/automation/schedules/{id}/pause`: Temporarily pause an active schedule.
- `PATCH /api/v1/automation/schedules/{id}/resume`: Resume a paused schedule and recalculate `next_run_at`.
- `DELETE /api/v1/automation/schedules/{id}`: Permanently delete a schedule and associated sweep history.
- `POST /api/v1/automation/schedules/{id}/trigger`: Instantly trigger an on-demand research sweep.
- `GET /api/v1/automation/schedules/{id}/sweeps`: List historical sweep results, novelty diffs, and novel claims.
- `GET /api/v1/automation/alerts`: List alerts across all scheduled research with unread filtering.
- `PATCH /api/v1/automation/alerts/{id}/acknowledge`: Mark an alert as acknowledged and read.
- `GET /api/v1/automation/metrics`: Retrieve aggregate automation metrics (active schedules, total sweeps, pending alerts, avg novelty score).

---

## 11. Adversarial Multi-Agent Debate Schema & REST Endpoints (Phase 27)

### 11.1 Table: `agent_debates`
Multi-agent dialectical debate sessions between affirmative thesis defense (`proposer`) and adversarial scrutiny (`opposer`).

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | Unique debate session ID |
| `user_id` | `UUID` | `FOREIGN KEY (users.id ON DELETE CASCADE), NOT NULL, INDEX` | Creator / owning user |
| `workspace_id` | `UUID` | `FOREIGN KEY (workspaces.id ON DELETE CASCADE), NULLABLE, INDEX` | Scoped workspace |
| `project_id` | `UUID` | `FOREIGN KEY (projects.id ON DELETE SET NULL), NULLABLE, INDEX` | Scoped project |
| `topic` | `VARCHAR(500)` | `NOT NULL` | Debate subject / topic |
| `initial_thesis` | `TEXT` | `NOT NULL` | Affirmative proposition defended by Proposer |
| `counter_thesis` | `TEXT` | `NULLABLE` | Opposing antithesis defended by Opposer |
| `status` | `VARCHAR(50)` | `NOT NULL, DEFAULT 'active', INDEX` | State (`active`, `concluded`, `abandoned`) |
| `max_rounds` | `INTEGER` | `NOT NULL, DEFAULT 3` | Maximum dialectical interaction rounds |
| `current_round` | `INTEGER` | `NOT NULL, DEFAULT 0` | Current completed round index |
| `proposer_model` | `VARCHAR(100)` | `NOT NULL, DEFAULT 'gemini-2.5-pro'` | Model backing ProposerAgent |
| `opposer_model` | `VARCHAR(100)` | `NOT NULL, DEFAULT 'gemini-2.5-pro'` | Model backing OpposerAgent |
| `arbiter_model` | `VARCHAR(100)` | `NOT NULL, DEFAULT 'gemini-2.5-pro'` | Model backing ConsensusArbiter |
| `proposer_elo` | `FLOAT` | `NOT NULL, DEFAULT 1500.0` | Proposer argument strength Elo rating |
| `opposer_elo` | `FLOAT` | `NOT NULL, DEFAULT 1500.0` | Opposer argument strength Elo rating |
| `config_json` | `JSONB / JSON` | `NULLABLE` | Configuration parameters (k-factor, temperature) |
| `created_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Creation timestamp |
| `updated_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Last modification timestamp |

---

### 11.2 Table: `debate_rounds`
Sequential dialectical rounds capturing arguments, rebuttals, citations, arbiter critiques, and round Elo shifts.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | Unique debate round ID |
| `debate_id` | `UUID` | `FOREIGN KEY (agent_debates.id ON DELETE CASCADE), NOT NULL, INDEX` | Parent debate ID |
| `round_number` | `INTEGER` | `NOT NULL` | Chronological round index (1-based) |
| `proposer_argument` | `TEXT` | `NOT NULL` | Affirmative argument text with deductions |
| `opposer_argument` | `TEXT` | `NOT NULL` | Adversarial counterargument and rebuttal |
| `proposer_citations`| `JSONB / JSON` | `NOT NULL, DEFAULT '[]'` | Empirical citations supporting proposer |
| `opposer_citations` | `JSONB / JSON` | `NOT NULL, DEFAULT '[]'` | Evidence supporting counterarguments |
| `proposer_score` | `FLOAT` | `NOT NULL, DEFAULT 0.8` | Arbiter round quality score for proposer $\in [0, 1]$ |
| `opposer_score` | `FLOAT` | `NOT NULL, DEFAULT 0.8` | Arbiter round quality score for opposer $\in [0, 1]$ |
| `arbiter_critique` | `TEXT` | `NOT NULL` | Impartial arbiter reasoning and evaluation |
| `round_winner` | `VARCHAR(50)` | `NOT NULL, DEFAULT 'draw'` | Outcome (`proposer`, `opposer`, `draw`) |
| `elo_delta` | `FLOAT` | `NOT NULL, DEFAULT 0.0` | Rating shift applied to winner/loser |
| `round_telemetry` | `JSONB / JSON` | `NOT NULL, DEFAULT '{}'` | Claims extracted, flaws, and concessions |
| `created_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Round timestamp |

---

### 11.3 Table: `debate_consensus`
Synthesized dialectical consensus reconciling opposing viewpoints into verified empirical claims, concessions, and residual uncertainties.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | Unique consensus ID |
| `debate_id` | `UUID` | `FOREIGN KEY (agent_debates.id ON DELETE CASCADE), NOT NULL, UNIQUE, INDEX` | Parent debate session |
| `consensus_statement` | `TEXT` | `NOT NULL` | Unified balanced scientific consensus |
| `accepted_claims` | `JSONB / JSON` | `NOT NULL, DEFAULT '[]'` | Claims surviving adversarial scrutiny |
| `refuted_claims` | `JSONB / JSON` | `NOT NULL, DEFAULT '[]'` | Claims invalidated or constrained |
| `concessions` | `JSONB / JSON` | `NOT NULL, DEFAULT '[]'` | Mutual concessions made during rounds |
| `remaining_uncertainties` | `JSONB / JSON` | `NOT NULL, DEFAULT '[]'` | Open empirical questions for future inquiry |
| `overall_confidence`| `FLOAT` | `NOT NULL, DEFAULT 0.85` | Factual confidence rating $\in [0, 1]$ |
| `winner_overall` | `VARCHAR(50)` | `NOT NULL, DEFAULT 'balanced_consensus'` | Overall verdict (`proposer_favored`, `opposer_favored`, `balanced_consensus`) |
| `final_proposer_elo`| `FLOAT` | `NOT NULL` | Concluding Elo of proposer |
| `final_opposer_elo` | `FLOAT` | `NOT NULL` | Concluding Elo of opposer |
| `synthesis_metadata`| `JSONB / JSON` | `NOT NULL, DEFAULT '{}'` | Arbiter telemetry and round summary stats |
| `created_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Synthesis timestamp |

---

### 11.4 REST Endpoints (Phase 27)

- `POST /api/v1/debates`: Launch a new adversarial multi-agent debate session with custom models, max rounds, topic, and thesis.
- `GET /api/v1/debates`: List debates with optional filtering by status, workspace, and project.
- `GET /api/v1/debates/{id}`: Retrieve comprehensive details of a debate including all chronological rounds and final consensus.
- `POST /api/v1/debates/{id}/rounds`: Execute the next dialectical round or trigger autonomous execution to completion (`run_to_completion: true`).
- `GET /api/v1/debates/{id}/rounds`: Retrieve full chronological transcript and citations for all rounds of a debate.
- `GET /api/v1/debates/{id}/consensus`: Fetch synthesized dialectical consensus statement and accepted/refuted claim lists.
- `GET /api/v1/debates/metrics`: Retrieve aggregate debate statistics (total debates, active debates, mean consensus confidence, average Proposer/Opposer Elo).
- `DELETE /api/v1/debates/{id}`: Permanently delete a debate session and all child round and consensus records.

---

## 12. Systematic Literature Review & PRISMA Meta-Analysis Schema & REST Endpoints (Phase 28)

### 12.1 Table: `literature_reviews`
Master systematic literature review (SLR) study records tracking search strings, PRISMA stages, and overall review status.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | Unique review ID |
| `user_id` | `UUID` | `FOREIGN KEY (users.id ON DELETE CASCADE), NOT NULL, INDEX` | Creator / owning user |
| `workspace_id` | `UUID` | `FOREIGN KEY (workspaces.id ON DELETE CASCADE), NULLABLE, INDEX` | Scoped workspace |
| `project_id` | `UUID` | `FOREIGN KEY (projects.id ON DELETE SET NULL), NULLABLE, INDEX` | Scoped project |
| `title` | `VARCHAR(500)` | `NOT NULL` | Systematic review title |
| `search_query` | `TEXT` | `NOT NULL` | Formal search syntax / boolean query |
| `status` | `VARCHAR(50)` | `NOT NULL, DEFAULT 'draft', INDEX` | State (`draft`, `screening`, `meta_analysis`, `completed`) |
| `prisma_stage` | `VARCHAR(50)` | `NOT NULL, DEFAULT 'identification'` | Current PRISMA 2020 stage |
| `metadata_json` | `JSONB / JSON` | `NULLABLE` | Review protocol details |
| `created_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Creation timestamp |
| `updated_at` | `TIMESTAMP WITH TZ` | `NOT NULL, DEFAULT NOW()` | Last update timestamp |

### 12.2 Tables: `slr_criteria`, `slr_study_candidates`, `meta_analysis_reports`, `risk_of_bias_assessments`
- `slr_criteria`: Inclusion and exclusion eligibility criteria (`criterion_type`, `description`, `field_target`).
- `slr_study_candidates`: Candidate papers evaluated against PRISMA flow (`title`, `authors`, `abstract`, `screening_status`, `exclusion_reason`, `effect_size`).
- `meta_analysis_reports`: Statistical pooling results (Cohen's $d$, Hedges' $g$, inverse-variance weights, Forest plot data points, Cochran's $Q$, $I^2$ heterogeneity).
- `risk_of_bias_assessments`: Cochrane RoB 2 multi-domain scores (`randomization_bias`, `deviations_bias`, `missing_data_bias`, `measurement_bias`, `reporting_bias`, `overall_bias`).

### 12.3 REST Endpoints (Phase 28)
- `POST /api/v1/literature/reviews`: Create systematic review protocol.
- `GET /api/v1/literature/reviews`: List reviews.
- `GET /api/v1/literature/reviews/{id}`: Fetch review with candidates, criteria, and meta-analysis.
- `POST /api/v1/literature/reviews/{id}/studies`: Add candidate studies.
- `POST /api/v1/literature/reviews/{id}/meta-analysis`: Run statistical pooling.
- `GET /api/v1/literature/metrics`: Query platform literature KPIs.

---

## 13. In-Silico Experimentation & Reproducibility Schema & REST Endpoints (Phase 29)

### 13.1 Tables: `experiment_protocols`, `reproducibility_runs`, `claim_verification_traces`
- `experiment_protocols`: Scientific computational experiments (`code_snippet`, `target_hypothesis`, `runtime_environment`, `allowed_modules`, `timeout_seconds`).
- `reproducibility_runs`: Sandboxed execution runs (`execution_status`, `stdout_output`, `stderr_output`, `return_value_json`, `execution_time_ms`, `replication_verdict`).
- `claim_verification_traces`: Exact claim vs execution comparisons (`target_claim`, `expected_value`, `observed_value`, `delta_metric`, `tolerance_threshold`, `passed_verification`).

### 13.2 REST Endpoints (Phase 29)
- `POST /api/v1/reproducibility/protocols`: Create experiment protocol.
- `POST /api/v1/reproducibility/protocols/{id}/execute`: Run sandboxed in-silico replication.
- `GET /api/v1/reproducibility/runs/{id}`: Fetch detailed replication trace and console logs.
- `GET /api/v1/reproducibility/metrics`: Query platform reproducibility metrics.

---

## 14. Multimodal Presentation & Executive Podcasting Schema & REST Endpoints (Phase 30)

### 14.1 Tables: `synthesis_presentations`, `presentation_slides`, `podcast_briefings`
- `synthesis_presentations`: Presentation slide deck records (`title`, `topic`, `target_audience`, `aspect_ratio`, `theme_palette`, `total_slides`).
- `presentation_slides`: Individual 16:9 slides (`slide_number`, `slide_type`, `title`, `headline`, `bullets_json`, `visual_cards_json`, `speaker_notes`).
- `podcast_briefings`: Executive audio dialogue scripts (`title`, `host_name`, `analyst_name`, `dialogue_script_json`, `duration_estimated_seconds`).

### 14.2 REST Endpoints (Phase 30)
- `POST /api/v1/presentations`: Generate structured 16:9 presentation deck.
- `GET /api/v1/presentations/{id}`: Fetch presentation with slides.
- `POST /api/v1/presentations/podcasts`: Generate multi-speaker podcast audio script.
- `GET /api/v1/presentations/metrics`: Query presentation and briefing metrics.

---

## 15. Autonomous Peer Review & Academic Publishing Schema & REST Endpoints (Phase 31)

### 15.1 Tables: `peer_review_manuscripts`, `peer_review_reports`, `manuscript_revisions`
- `peer_review_manuscripts`: Academic manuscripts (`title`, `abstract`, `full_manuscript_text`, `manuscript_type`, `editorial_status`, `doi_identifier`, `latex_source`, `bibtex_entries`).
- `peer_review_reports`: Double-blind referee scorecards (`reviewer_persona`, `overall_recommendation`, `soundness_score`, `novelty_score`, `clarity_score`, `reproducibility_score`, `detailed_comments`).
- `manuscript_revisions`: Author revision cycles and rebuttals (`revision_number`, `author_rebuttal_letter`, `point_by_point_responses_json`, `diff_summary`).

### 15.2 REST Endpoints (Phase 31)
- `POST /api/v1/publishing/manuscripts`: Submit manuscript for peer review.
- `POST /api/v1/publishing/manuscripts/{id}/review`: Run double-blind referee review panel.
- `POST /api/v1/publishing/manuscripts/{id}/revisions`: Submit author revision & point-by-point rebuttal.
- `POST /api/v1/publishing/manuscripts/{id}/publish`: Generate camera-ready preprint (LaTeX, BibTeX, DOI).
- `GET /api/v1/publishing/metrics`: Query platform publishing KPIs.

---

## 16. Real-Time Collaborative Research Canvas Schema & REST Endpoints (Phase 32)

### 16.1 Tables: `canvas_boards`, `canvas_nodes`, `canvas_edges`
- `canvas_boards`: 2D spatial canvas boards (`title`, `description`, `viewport_settings_json`, `grid_type`).
- `canvas_nodes`: Visual canvas node elements (`node_type`, `label`, `content`, `position_x`, `position_y`, `width`, `height`, `confidence_score`, `color_accent`, `metadata_json`).
- `canvas_edges`: Relational edge connectors (`source_node_id`, `target_node_id`, `relation_type`, `label`, `weight`, `is_directed`).

### 16.2 REST Endpoints (Phase 32)
- `POST /api/v1/canvas/boards`: Create canvas board.
- `GET /api/v1/canvas/boards/{id}`: Fetch complete board with nodes and edges.
- `POST /api/v1/canvas/boards/{id}/generate`: Auto-generate 2D DAG layout from research findings.
- `POST /api/v1/canvas/boards/{id}/nodes`: Add visual node.
- `PATCH /api/v1/canvas/boards/{id}/nodes/{node_id}`: Update node position and content.
- `POST /api/v1/canvas/boards/{id}/edges`: Add relational edge connector.
- `POST /api/v1/canvas/boards/{id}/brainstorm`: Trigger AI agent brainstorming expansion.
- `GET /api/v1/canvas/metrics`: Query platform canvas metrics.

---

## 17. Synthetic Instruction Dataset Generation Schema & REST Endpoints (Phase 33)

### 17.1 Tables: `synthetic_datasets`, `instruction_samples`, `alignment_exports`
- `synthetic_datasets`: Fine-tuning instruction dataset records (`name`, `dataset_format`, `domain_field`, `target_model_family`, `total_samples`, `quality_filter_threshold`, `status`).
- `instruction_samples`: Instruction sample records (`sample_index`, `system_prompt`, `instruction`, `input_context`, `chosen_response`, `rejected_response`, `cot_reasoning_trace`, `evolution_strategy`, `quality_score`, `curation_verdict`).
- `alignment_exports`: Standardized fine-tuning export files (`export_format`, `sample_count`, `file_size_bytes`, `exported_at`).

### 17.2 REST Endpoints (Phase 33)
- `POST /api/v1/datasets/synthesize`: Synthesize instruction dataset from research findings.
- `GET /api/v1/datasets`: List synthetic datasets.
- `GET /api/v1/datasets/{id}`: Fetch dataset with instruction samples and exports.
- `PATCH /api/v1/datasets/{id}/samples/{sample_id}`: Active learning human curation (accept, reject, edit).
- `POST /api/v1/datasets/{id}/export`: Standardized JSONL export.
- `GET /api/v1/datasets/metrics`: Query platform dataset metrics.

---

## 18. Autonomous Patent Landscape Analysis & Prior Art Schema & REST Endpoints (Phase 34)

### 18.1 Tables: `patent_corpora`, `patent_documents`, `patent_claims`, `prior_art_evaluations`, `fto_reports`
- `patent_corpora`: Master patent landscape study (`title`, `technology_domain`, `cpc_classification`, `jurisdiction`, `status`, `freedom_to_operate_verdict`).
- `patent_documents`: Patent asset records (`patent_number`, `title`, `abstract`, `assignee`, `filing_date`, `publication_date`, `cpc_classes`, `status`).
- `patent_claims`: Granular claim breakdown (`claim_number`, `claim_type`, `parent_claim_number`, `claim_text`, `parsed_elements_json`, `infringement_risk_score`).
- `prior_art_evaluations`: 35 U.S.C. 102/103 evaluation traces (`target_invention_claim`, `novelty_score`, `obviousness_score`, `verdict`, `detailed_rationale`, `mitigation_strategy`).
- `fto_reports`: Freedom-to-Operate clearance dossiers (`total_examined_patents`, `fto_clearance_percentage`, `summary_assessment`, `white_space_opportunities`, `claim_chart_matrices`).

### 18.2 REST Endpoints (Phase 34)
- `POST /api/v1/patents/corpora`: Create patent landscape study and index baseline prior art patents.
- `GET /api/v1/patents/corpora`: List patent corpora.
- `GET /api/v1/patents/corpora/{id}`: Fetch complete corpus with patents, claims, evaluations, and FTO reports.
- `POST /api/v1/patents/corpora/{id}/evaluate-claim`: Run 102/103 prior art evaluation against target invention claim.
- `POST /api/v1/patents/corpora/{id}/fto-report`: Generate Freedom to Operate clearance report and white-space map.
- `GET /api/v1/patents/metrics`: Query platform patent KPIs.
- `DELETE /api/v1/patents/corpora/{id}`: Delete corpus.

---

## 19. Autonomous Scientific Grant Proposal Synthesizer Schema & REST Endpoints (Phase 35)

### 19.1 Tables: `grant_proposals`, `grant_specific_aims`, `grant_budget_items`, `grant_review_scorecards`
- `grant_proposals`: Master grant proposal project (`title`, `funding_agency`, `grant_mechanism`, `target_call_number`, `project_duration_years`, `total_requested_budget_usd`, `indirect_cost_rate_percent`, `status`, `executive_abstract`, `significance_narrative`, `innovation_narrative`, `approach_narrative`, `preliminary_data_summary`, `mock_panel_overall_score`, `percentile_estimate`, `metadata_json`).
- `grant_specific_aims`: Specific Aim work packages (`aim_number`, `title`, `hypothesis`, `experimental_design`, `expected_outcomes`, `potential_pitfalls_and_alternatives`, `milestones_json`, `allocated_effort_percent`).
- `grant_budget_items`: Itemized financial lines (`year_number`, `category`, `item_name`, `cost_usd`, `justification`, `is_direct_cost`).
- `grant_review_scorecards`: Mock study section reviews (`reviewer_persona`, `significance_score`, `investigators_score`, `innovation_score`, `approach_score`, `environment_score`, `overall_impact_score`, `recommendation`, `critique_strengths`, `critique_weaknesses`, `summary_statement`).

### 19.2 REST Endpoints (Phase 35)
- `POST /api/v1/grants/proposals`: Create grant proposal project and synthesize baseline aims and budget.
- `GET /api/v1/grants/proposals`: List grant proposals.
- `GET /api/v1/grants/proposals/{id}`: Fetch complete proposal with aims, budget, and mock reviews.
- `POST /api/v1/grants/proposals/{id}/synthesize-aims`: Synthesize Specific Aims from research topic.
- `POST /api/v1/grants/proposals/{id}/calculate-budget`: Recalculate multi-year institutional budget.
- `POST /api/v1/grants/proposals/{id}/mock-review`: Run autonomous study section peer review simulation.
- `GET /api/v1/grants/proposals/{id}/export-latex`: Export proposal as compilable LaTeX document.
- `GET /api/v1/grants/metrics`: Query platform grant funding metrics.
- `DELETE /api/v1/grants/proposals/{id}`: Delete proposal.

---

## 20. Autonomous Clinical Trial Protocol & Drug Repurposing Schema & REST Endpoints (Phase 36)

### 20.1 Tables: `clinical_protocols`, `clinical_cohort_criteria`, `clinical_drug_candidates`, `clinical_regulatory_packages`
- `clinical_protocols`: Master clinical trial protocol (`id`, `user_id`, `workspace_id`, `project_id`, `protocol_title`, `phase_type`, `disease_indication`, `icd_code`, `investigational_agent`, `mechanism_of_action`, `target_gene_or_protein`, `primary_endpoint`, `secondary_endpoints`, `sample_size_planned`, `study_duration_weeks`, `adverse_risk_score`, `regulatory_status`, `full_protocol_json`, `created_at`, `updated_at`).
- `clinical_cohort_criteria`: PICO patient eligibility criteria (`id`, `protocol_id`, `criterion_type`, `category`, `description`, `is_mandatory`, `loinc_code`).
- `clinical_drug_candidates`: Repurposed drug screening candidate (`id`, `protocol_id`, `compound_name`, `smiles_string`, `current_approved_indication`, `repurposed_indication`, `binding_affinity_nm`, `bioavailability_pct`, `toxicity_risk_score`, `repurposing_rationale`, `created_at`).
- `clinical_regulatory_packages`: eCTD IND / EMA CTD electronic regulatory submission dossier (`id`, `protocol_id`, `regulatory_agency`, `module_type`, `completeness_score`, `irb_readiness_verdict`, `validation_findings`, `generated_at`).

### 20.2 REST Endpoints (Phase 36)
- `POST /api/v1/clinical/protocols/generate`: Autonomous generation and persistence of clinical protocol, cohort criteria, candidate screens, and initial FDA IND package.
- `GET /api/v1/clinical/protocols`: List clinical protocols with filters for workspace/project.
- `GET /api/v1/clinical/protocols/{id}`: Retrieve detailed protocol with cohort criteria, drug candidates, and regulatory packages.
- `POST /api/v1/clinical/protocols/{id}/criteria`: Add custom PICO cohort inclusion or exclusion criterion.
- `POST /api/v1/clinical/protocols/{id}/regulatory-package`: Generate electronic regulatory module dossier.

---

## 21. Autonomous Laboratory Automation & Robotic Protocol Schema & REST Endpoints (Phase 37)

### 21.1 Tables: `robotic_protocols`, `robotic_deck_slots`, `robotic_transfer_steps`, `robotic_execution_traces`
- `robotic_protocols`: Master robotic protocol (`id`, `user_id`, `workspace_id`, `project_id`, `protocol_name`, `robot_platform`, `assay_type`, `deck_layout_json`, `total_runtime_minutes`, `liquid_waste_volume_ml`, `validation_status`, `protocol_python_code`, `autoprotocol_json`, `created_at`, `updated_at`).
- `robotic_deck_slots`: Workstation 12-slot deck allocations (`id`, `protocol_id`, `slot_number`, `labware_type`, `reagent_name`, `initial_volume_ul`, `current_volume_ul`).
- `robotic_transfer_steps`: Atomic pipetting transfers (`id`, `protocol_id`, `step_index`, `source_slot`, `source_well`, `target_slot`, `target_well`, `volume_ul`, `pipette_name`, `transfer_type`, `liquid_class`).
- `robotic_execution_traces`: Virtual physics simulation & collision telemetry (`id`, `protocol_id`, `step_count`, `simulated_runtime_sec`, `estimated_tip_count`, `tip_waste_pct`, `collision_warnings`, `simulation_log`, `executed_at`).

### 21.2 REST Endpoints (Phase 37)
- `POST /api/v1/lab/protocols/compile`: Autonomous compilation, virtual collision check, and protocol persistence.
- `GET /api/v1/lab/protocols`: List robotic protocols with filters for platform, workspace, and project.
- `GET /api/v1/lab/protocols/{id}`: Retrieve detailed protocol with deck slots, transfer steps, and simulation traces.
- `POST /api/v1/lab/protocols/{id}/simulate`: Dynamic simulation of custom pipetting sequences and collision evaluation.
- `GET /api/v1/lab/protocols/{id}/export-code`: Multi-format robot code export (`opentrons_python`, `pylabrobot`, `autoprotocol`).

---

## 22. Autonomous Bio-Molecular Structure & Protein Folding Schema & REST Endpoints (Phase 38)

### 22.1 Tables: `molecular_structures`, `binding_pockets`, `docking_poses`, `mutation_stabilities`
- `molecular_structures`: Master 3D molecular structure specification (`id`, `user_id`, `workspace_id`, `project_id`, `uniprot_id`, `gene_name`, `organism`, `sequence`, `mean_plddt_score`, `resolution_angstrom`, `structure_source`, `pdb_coordinate_data`, `secondary_structure_summary`, `created_at`, `updated_at`).
- `binding_pockets`: Predicted catalytic and allosteric active sites (`id`, `structure_id`, `pocket_index`, `druggability_score`, `volume_cubic_angstrom`, `surface_area_angstrom2`, `key_residues_json`, `center_coordinates_json`).
- `docking_poses`: In-silico ligand docking results (`id`, `structure_id`, `pocket_id`, `ligand_name`, `binding_affinity_kcal_mol`, `rmsd_angstrom`, `hydrogen_bonds_count`, `pi_stacking_interactions`, `pose_coordinates_json`, `created_at`).
- `mutation_stabilities`: Thermodynamic folding free energy shift scans ($\Delta\Delta G$) (`id`, `structure_id`, `wildtype_residue`, `position`, `mutant_residue`, `delta_delta_g_kcal_mol`, `stability_verdict`, `pathogenicity_score`, `created_at`).

### 22.2 REST Endpoints (Phase 38)
- `POST /api/v1/molecular/predict`: Predict 3D protein structure coordinates, pLDDT confidence spectrum, and binding pockets.
- `GET /api/v1/molecular/structures`: List molecular structures with pocket counts and pLDDT scores.
- `GET /api/v1/molecular/structures/{id}`: Retrieve full molecular structure with 3D coordinates, pockets, docking poses, and mutations.
- `POST /api/v1/molecular/structures/{id}/dock`: Execute in-silico ligand docking against predicted binding pocket.
- `POST /api/v1/molecular/structures/{id}/mutate`: Execute thermodynamic mutational stability scan ($\Delta\Delta G$).
- `GET /api/v1/molecular/structures/{id}/export-pdb`: Download 3D PDB coordinate file.

---

## 23. Autonomous Molecular Dynamics & Quantum Chemistry Schema & REST Endpoints (Phase 39)

### 23.1 Tables: `md_simulations`, `md_trajectory_frames`, `md_residue_fluctuations`, `md_quantum_properties`
- `md_simulations`: Master atomistic molecular dynamics simulation run (`id`, `user_id`, `workspace_id`, `project_id`, `uniprot_id`, `system_name`, `organism`, `forcefield`, `solvent_model`, `ensemble`, `total_frames`, `timestep_ps`, `total_duration_ns`, `temperature_kelvin`, `pressure_bar`, `equilibrium_rmsd_angstrom`, `thermodynamic_data_json`, `created_at`, `updated_at`).
- `md_trajectory_frames`: Time-series coordinate checkpoints (`id`, `simulation_id`, `frame_index`, `timestamp_ps`, `rmsd_angstrom`, `radius_of_gyration_angstrom`, `potential_energy_kj_mol`, `kinetic_energy_kj_mol`, `total_energy_kj_mol`, `temperature_kelvin`, `frame_pdb_coordinates`).
- `md_residue_fluctuations`: Per-residue dynamic flexibility profile (`id`, `simulation_id`, `residue_number`, `residue_name`, `rmsf_angstrom`, `b_factor_equivalent`, `is_flexible_loop`, `secondary_structure_type`).
- `md_quantum_properties`: Density Functional Theory (DFT) quantum electronic orbital descriptors (`id`, `simulation_id`, `dft_method`, `homo_energy_ev`, `lumo_energy_ev`, `bandgap_energy_ev`, `dipole_moment_debye`, `polarizability_angstrom3`, `total_scf_energy_hartree`, `mulliken_partial_charges_json`, `electrostatic_potential_surface_json`, `created_at`).

### 23.2 REST Endpoints (Phase 39)
- `POST /api/v1/md/simulate`: Execute all-atom MD trajectory integration, calculate RMSD convergence, RMSF flexibility, and DFT HOMO/LUMO bandgap.
- `GET /api/v1/md/simulations`: List simulations with summary stats and bandgaps.
- `GET /api/v1/md/simulations/{id}`: Detailed simulation inspection with full trajectory frames, fluctuations, and quantum properties.
- `GET /api/v1/md/simulations/{id}/frames/{frame_index}`: Fetch single coordinate snapshot.
- `GET /api/v1/md/simulations/{id}/export-trajectory`: Download concatenated multi-model PDB trajectory file.








