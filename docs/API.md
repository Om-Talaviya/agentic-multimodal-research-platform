# API Design

## Overview

RESTful API for the research platform with clear resource-oriented endpoints.

## Base URL

```
/api/v1
```

## Authentication

JWT Bearer tokens are implemented in `packages/shared/auth.py` and `apps/api/src/api/routes/auth.py` with Role-Based Access Control (`Admin`, `Researcher`, `Viewer`). Endpoints support bearer authorization headers.

## Endpoints

### Research Jobs

#### Create Research Job
```http
POST /api/v1/research
Content-Type: application/json

{
  "question": "What are the environmental impacts of lithium mining?",
  "context": "Focus on South America",
  "constraints": ["peer-reviewed sources only", "last 5 years"],
  "preferred_sources": ["academic", "government"]
}
```

Response: `201 Created`
```json
{
  "id": "uuid",
  "request_id": "uuid",
  "question": "What are the environmental impacts of lithium mining?",
  "objective": "Analyze environmental impacts of lithium mining in South America",
  "domain": "environmental science",
  "scope": "South America, last 5 years",
  "constraints": ["peer-reviewed sources only", "last 5 years"],
  "expected_output": "report",
  "status": "pending",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Get Research Job
```http
GET /api/v1/research/{job_id}
```

Response: `200 OK`
```json
{
  "id": "uuid",
  "request_id": "uuid",
  "question": "...",
  "objective": "...",
  "domain": "...",
  "scope": "...",
  "constraints": [...],
  "expected_output": "report",
  "status": "running",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:31:00Z",
  "completed_at": null,
  "progress": {
    "total_tasks": 5,
    "completed_tasks": 2,
    "failed_tasks": 0,
    "current_step": "web_research"
  }
}
```

#### List Research Jobs
```http
GET /api/v1/research?limit=20&offset=0&status=completed
```

#### Get Research Plan
```http
GET /api/v1/research/{job_id}/plan
```

Response:
```json
{
  "objective": "...",
  "steps": [
    {
      "id": "step_1",
      "name": "Web Research",
      "description": "Search for recent studies on lithium mining impacts",
      "agent": "web_research",
      "inputs": {"query": "lithium mining environmental impacts South America 2020-2024"},
      "depends_on": [],
      "priority": 1
    },
    {
      "id": "step_2",
      "name": "Document Analysis",
      "description": "Analyze uploaded EPA reports",
      "agent": "document_analysis",
      "inputs": {"document_ids": ["doc-uuid-1"]},
      "depends_on": [],
      "priority": 1
    },
    {
      "id": "step_3",
      "name": "Synthesis",
      "description": "Combine findings from all sources",
      "agent": "synthesis",
      "inputs": {},
      "depends_on": ["step_1", "step_2"],
      "priority": 2
    }
  ],
  "expected_outputs": ["report"]
}
```

#### Get Research Tasks
```http
GET /api/v1/research/{job_id}/tasks
```

Response:
```json
{
  "tasks": [
    {
      "id": "uuid",
      "job_id": "uuid",
      "type": "web_research",
      "objective": "Search for recent studies...",
      "agent": "web_research",
      "status": "completed",
      "started_at": "2024-01-15T10:30:15Z",
      "completed_at": "2024-01-15T10:32:00Z",
      "result": {"sources_found": 12, "evidence_count": 45}
    }
  ]
}
```

#### Get Sources
```http
GET /api/v1/research/{job_id}/sources
```

Response:
```json
{
  "sources": [
    {
      "id": "uuid",
      "type": "web",
      "url": "https://example.com/study",
      "title": "Environmental Impact of Lithium Mining in Chile",
      "metadata": {"domain": "example.com", "date": "2023-06-15"},
      "retrieved_at": "2024-01-15T10:31:00Z"
    }
  ]
}
```

#### Get Evidence
```http
GET /api/v1/research/{job_id}/evidence
```

Response:
```json
{
  "evidence": [
    {
      "id": "uuid",
      "source_id": "uuid",
      "claim": "Lithium mining consumes 500,000 gallons of water per ton",
      "supporting_text": "According to the study, lithium extraction requires...",
      "confidence": 0.85,
      "verification_status": "consensus",
      "verification_notes": "Confirmed by 3 independent sources"
    }
  ]
}
```

#### Get Report
```http
GET /api/v1/research/{job_id}/report
```

Response:
```json
{
  "id": "uuid",
  "job_id": "uuid",
  "title": "Environmental Impacts of Lithium Mining in South America",
  "executive_summary": "This research analyzes...",
  "methodology": "Web research, document analysis, synthesis...",
  "findings": [
    {
      "id": "uuid",
      "topic": "Water Consumption",
      "summary": "Lithium mining consumes significant water resources...",
      "evidence_ids": ["uuid-1", "uuid-2"],
      "confidence": 0.88,
      "uncertainty": "Regional variations not fully captured",
      "assumptions": ["Current extraction methods"]
    }
  ],
  "evidence": [...],
  "sources": [...],
  "conclusions": ["Lithium mining has significant water impacts..."],
  "limitations": ["Limited to English-language sources"],
  "generated_at": "2024-01-15T10:35:00Z"
}
```

#### Research Progress WebSocket Stream
```http
GET /api/v1/research/{job_id}/ws?token={access_token}
```

Frames:
1. **Initial Snapshot** (`type: "snapshot"`): Delivers full job state, tasks, sources, evidence, and report.
2. **Live Events** (`type: "event"`): Streams real-time task progress, evidence discovery, and verification events.
3. **Heartbeat** (`type: "heartbeat"`): Periodic keep-alive frames on idle connections.

### Documents


#### Upload Document
```http
POST /api/v1/documents
Content-Type: multipart/form-data

file: <binary>
research_job_id: uuid (optional)
```

Response: `201 Created`
```json
{
  "id": "uuid",
  "filename": "report.pdf",
  "mime_type": "application/pdf",
  "file_size": 2048576,
  "status": "processing",
  "created_at": "2024-01-15T10:25:00Z"
}
```

#### Get Document
```http
GET /api/v1/documents/{document_id}
```

#### List Documents
```http
GET /api/v1/documents?job_id={job_id}&limit=20
```

### Models

#### List Available Models
```http
GET /api/v1/models
```

Response:
```json
{
  "providers": [
    {
      "name": "ollama",
      "type": "local",
      "models": [
        {"name": "llama3.1", "capabilities": ["reasoning", "coding", "summarization"]},
        {"name": "llava", "capabilities": ["vision", "reasoning"]},
        {"name": "nomic-embed-text", "capabilities": ["embeddings"]}
      ]
    }
  ]
}
```

### Health

#### Health Check
```http
GET /api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "checks": {
    "database": "healthy",
    "vector_store": "healthy",
    "model_providers": {
      "ollama": "healthy"
    }
  }
}
```

### WebSocket (Real-time Updates)

```http
GET /api/v1/research/{job_id}/stream
```

Server-sent events:
```json
event: task_started
data: {"task_id": "uuid", "agent": "web_research"}

event: task_completed
data: {"task_id": "uuid", "agent": "web_research", "result": {...}}

event: job_completed
data: {"job_id": "uuid", "report_id": "uuid"}

event: job_failed
data: {"job_id": "uuid", "error": "..."}
```

## Error Responses

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request",
    "details": [
      {"field": "question", "message": "Question is required"}
    ]
  }
}
```

Common error codes:
- `VALIDATION_ERROR` - Request validation failed
- `NOT_FOUND` - Resource not found
- `CONFLICT` - Resource conflict
- `INTERNAL_ERROR` - Server error
- `PROVIDER_UNAVAILABLE` - Model provider unavailable
- `RATE_LIMITED` - Rate limit exceeded

## Rate Limiting

- 60 requests/minute per IP (configurable)
- Higher limits for authenticated users (future)

## Pagination

All list endpoints support:
- `limit` (default 20, max 100)
- `offset` (default 0)

Response includes:
```json
{
  "items": [...],
  "total": 150,
  "limit": 20,
  "offset": 0
}
```

---

*API versioned in URL. Breaking changes require new version.*