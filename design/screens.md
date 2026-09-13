# Screen Specifications & States: design/screens.md

This document details each screen layout, component tree, and dynamic UI states implemented in `apps/web/src/pages`.

---

## 1. Global Application Layout (`Layout.tsx`)

- **Header / App Bar**:
  - Logo with gradient brand accent: **Agentic Research**
  - Navigation tabs: `Dashboard` (FileText icon), `New Research` (Plus icon), `Settings` (Settings icon)
- **Main Viewport**:
  - Centered responsive container with standard horizontal padding and maximum width constraint (`1200px`).

---

## 2. Dashboard Screen (`Dashboard.tsx`)

### Components:
- **Header Action Bar**: Page title ("Research Jobs") + "New Research" primary CTA button.
- **Error Banner**: Rendered conditionally on network or server error.
- **Jobs Table**:
  - Columns: `Question`, `Status`, `Created`, `Actions`.
  - Truncated question title and objective preview.
  - Formatted localized date/time.
  - "View" outline button linking to `/research/:id`.

### Dynamic States:
| State | UI Representation |
|---|---|
| **Loading** | Centered animated spinner (`Loader2`). |
| **Empty State** | Large search icon, "No research jobs yet" heading, prompt copy, and "Start Research" CTA. |
| **Loaded Table** | Sorted list of jobs with color-coded status badges (`badge-pending`, `badge-running`, `badge-completed`, `badge-failed`). |
| **Error** | Red alert banner with error message. |

---

## 3. New Research Screen (`NewResearch.tsx`)

### Components:
- **Form Card**:
  - `Research Question` (Textarea, required, 4 rows).
  - `Additional Context` (Textarea, optional, 3 rows).
  - `Constraints` (Textarea, optional, 1 constraint per line, 3 rows).
  - `Submit Button` ("Start Research" with dynamic loading spinner during submission).
- **Helper Guide Card**:
  - Grid of four actionable research tips with checkmark icons.

### Dynamic States:
| State | UI Representation |
|---|---|
| **Idle** | Clean form ready for input. |
| **Submitting** | Textareas and button disabled; spinner active with "Starting research...". |
| **Success** | Green banner: "Research job created successfully!"; automatic redirection after 1000ms. |
| **Error** | Red alert banner detailing backend validation or connection error. |

---

## 4. Research Detail Screen (`ResearchDetail.tsx`)

### Components:
- **Job Header Bar**:
  - "Back" button returning to Dashboard.
  - Research Question title and Objective summary.
  - Overall status icon and badge (Pending: Clock/amber, Running: Loader2/blue animate-spin, Completed: CheckCircle/green, Failed: AlertCircle/red).
- **Navigation Tabs**:
  1. `Overview` (FlaskConical icon)
  2. `Plan` (Layers icon)
  3. `Tasks` (Search icon)
  4. `Sources` (FileText icon)
  5. `Evidence` (FileCheck icon)
  6. `Report` (FileText icon, disabled until report exists or job completes)
- **Tab Content Views**:
  - **Overview**: 4-card metric grid (Status, Domain, Created Date, Completed Tasks ratio) + constraint pills.
  - **Plan**: Strategic execution plan description.
  - **Tasks**: Table with columns `Task`, `Agent`, `Status`, `Started`, `Completed`.
  - **Sources**: Grid of source cards with title, type badge, clickable external URL, and retrieval timestamp.
  - **Evidence**: Cards listing atomic claims, confidence percentage badges, supporting quote excerpts, and verification status.
  - **Report**: Full markdown-styled synthesis document with Title, Executive Summary, Methodology, Topic Findings with confidence ratings, Conclusions, and Limitations.

### Dynamic States:
| State | UI Representation |
|---|---|
| **Initial Loading** | Centered animated spinner. |
| **Not Found** | Empty state card with alert icon and "Back to Dashboard" button. |
| **Streaming Active** | Live badge updates, task progress transitions, and live evidence card additions. |
| **Report Generating** | Centered spinner with "Report is being generated..." when job is completed but report synthesis is running. |

---

## 5. Settings Screen (`Settings.tsx`)

### Components:
- **Model Providers Card**:
  - Ollama URL input (`http://localhost:11434`).
  - Default LLM dropdown (`llama3.1`, `mistral`, `codellama`).
  - Default Vision model dropdown (`llava`, `bakllava`).
  - Default Embedding model dropdown (`nomic-embed-text`, `all-minilm`).
  - "Save Settings" button with status alert.
  - Ollama CLI helper notice.
- **General Settings Card**:
  - Log Level selector (`DEBUG`, `INFO`, `WARNING`, `ERROR`).
  - Max Upload Size (MB) numerical input.
