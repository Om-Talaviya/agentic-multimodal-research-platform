# User Interaction & Navigation Flows: design/user-flows.md

This document outlines the step-by-step user journeys and state transitions across the **Agentic Multimodal Research Platform** web interface.

---

## 1. Flow: Launching a New Research Inquiry

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Web as Web App (React)
    participant API as FastAPI Backend
    participant WS as WebSocket Channel
    participant Orchestrator as Research Pipeline

    User->>Web: Navigates to "/research/new"
    User->>Web: Enters Question, Context & Constraints
    User->>Web: Clicks "Start Research"
    Web->>API: POST /api/v1/research (Payload)
    API-->>Web: HTTP 201 Created (Returns Job ID)
    Web->>Web: Displays success alert & redirects to "/research/:id"
    Web->>WS: Connects to "/api/v1/research/:id/ws"
    WS-->>Web: Sends initial "snapshot" message
    API->>Orchestrator: Spawns background research pipeline
    Orchestrator->>WS: Emits real-time DAG events (task_started, evidence_added, etc.)
    WS-->>Web: Streams live updates to React state
```

---

## 2. Flow: Monitoring Real-Time Research Execution

1. **Connection Initialization**:
   - Web application mounts `ResearchDetail` component.
   - Triggers `fetchData()` via REST API as fallback baseline.
   - Initiates WebSocket handshake to `/api/v1/research/{id}/ws`.
2. **Snapshot Hydration**:
   - Server authenticates connection and delivers a complete initial state snapshot (`snapshot` type).
   - Client updates `job`, `tasks`, `sources`, `evidence`, and `report` states simultaneously.
3. **Live Event Stream Processing**:
   - `job_started` / `job_completed`: Updates overall header badge and timestamps.
   - `task_started` / `task_completed` / `task_failed`: Updates specific task row in the **Tasks** table with live status spinners.
   - `sources_added`: Appends new sources to the **Sources** tab.
   - `evidence_added` / `verification_completed`: Appends verified claims to the **Evidence** tab.
   - `report_generated`: Activates the **Report** tab and loads synthesized findings.
4. **Disconnection & Reconnection**:
   - If connection drops, an exponential backoff retry loop (1s, 2s, 4s, up to 10s) reconnects automatically.
   - Periodic 30-second server heartbeats prevent proxy timeouts.

---

## 3. Flow: Exploring Evidence & Final Report

```mermaid
graph TD
    A[User on Research Detail Page] --> B{Select Tab}
    B -->|Overview| C[View high-level metadata, domains, and progress stats]
    B -->|Tasks| D[Inspect DAG tasks, assigned agents, and execution runtimes]
    B -->|Sources| E[Review source URLs, types, and retrieval timestamps]
    B -->|Evidence| F[Review atomic claims, supporting text quotes, and confidence scores]
    B -->|Report| G[Read Executive Summary, Findings by Topic, Conclusions & Limitations]
```

---

## 4. Flow: Configuring System Settings

1. User navigates to `/settings`.
2. Modifies Ollama provider URL, default LLM model (`llama3.1`, `mistral`, `codellama`), Vision model (`llava`, `bakllava`), or Embedding model (`nomic-embed-text`, `all-minilm`).
3. Sets general logging levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`) and maximum upload limits.
4. Clicks **Save Settings** to persist local client preferences with confirmation banners.
