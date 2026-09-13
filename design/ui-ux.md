# Frontend Design & UI/UX Architecture: ui-ux.md

This document defines the complete visual design system, interaction patterns, user flows, and wireframe layouts for the **Agentic Multimodal Research Platform (AI Research Operating System)**.

---

## 1. Visual Design Philosophy & Principles

1. **AI Research Operating System (Not a Generic Chatbot)**: The interface is designed as an interactive research cockpit where complex Directed Acyclic Graph (DAG) state, multi-source evidence, and long-form synthesis reports are organized with high clarity and depth.
2. **Transparent Progression & Zero Black Box**: Every step of the agentic workflow is streamed live over WebSockets with granular step indicators, agent attribution, and execution metrics.
3. **Deep Explainability ("Why do you believe this?")**: Users can click any factual claim or chart in the final report to inspect the exact underlying evidence, confidence score, source document, and page/paragraph coordinates.
4. **Curated Aesthetic Standards**: Built with modern typography, refined dark mode palette, smooth gradients, subtle glassmorphism cards, and explicit state handling (Loading, Empty, Error, Active).

---

## 2. Design System Tokens (Vanilla CSS)

```css
:root {
  /* Color Palette */
  --bg-primary: #0a0e17;
  --bg-secondary: #111827;
  --bg-card: rgba(17, 24, 39, 0.85);
  --bg-glass: rgba(255, 255, 255, 0.04);
  --border-subtle: rgba(255, 255, 255, 0.08);
  --border-focus: #38bdf8;
  
  /* Brand & Accent Accents */
  --accent-blue: #38bdf8;
  --accent-purple: #818cf8;
  --accent-emerald: #34d399;
  --accent-amber: #fbbf24;
  --accent-rose: #f43f5e;

  /* Typography */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

  /* Shadows & Glassmorphism */
  --shadow-card: 0 4px 20px -2px rgba(0, 0, 0, 0.5);
  --shadow-glow: 0 0 15px rgba(56, 189, 248, 0.25);
  --blur-glass: blur(12px);
}
```

---

## 3. Platform Screen Breakdown & Layouts

### 3.1 Main Navigation & Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  [🔬 AI RESEARCH OS]   Dashboard   Research   Knowledge   Documents   Memory   Knowledge Graph   Projects ⚙️│
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│   🚀 Start New Autonomous Research                                                          │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ 💬 What do you want to research?                                                      │  │
│  │ [ Analyze whether biodegradable packaging can realistically replace conventional... ] │  │
│  │ ┌───────────────┐  ┌─────────────────────┐  ┌──────────────────┐  [ Launch Research →]│  │
│  │ │ 🌐 Live Web   │  │ 📚 Private Knowledge│  │ 📊 Data Analysis │                      │  │
│  │ └───────────────┘  └─────────────────────┘  └──────────────────┘                      │  │
│  └───────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                             │
│   📈 Recent Research Dossiers                         ⚡ System Health & Quota              │
│  ┌──────────────────────────────────────────────────┐ ┌───────────────────────────────────┐  │
│  │ • Sustainable Food Packaging 10-Yr Outlook (82%) │ │ Monthly Tokens: 142,500 / 500,000 │  │
│  │ • Solid-State Battery Commercialization (94%)    │ │ Active Model: Gemini 2.0 Flash    │  │
│  │ • Microplastic Filtration in Wastewater (88%)    │ │ Local Fallback: Ollama Llama 3.1  │  │
│  └──────────────────────────────────────────────────┘ └───────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.2 Live Research Progression Screen

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  ◄ Back to Dashboard    Job: Sustainable Food Packaging (ID: 8351-5d5a)    [● RUNNING]      │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│  [Overview] [Execution Plan] [Task DAG] [Sources (14)] [Evidence (28)] [Memories] [Report]  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│   LIVE AGENT PROGRESSION:                                                                   │
│   1. Understanding Request .................................................... [DONE 0.4s] │
│   2. Recalling Cross-Session Research Memory .................................. [DONE 0.2s] │
│   3. Planning & Subquestion Decomposition ..................................... [DONE 1.2s] │
│   4. Checking Private Knowledge Base (Found 3 PDFs) ........................... [DONE 0.8s] │
│   5. Retrieving Relevant Document Context ..................................... [DONE 0.5s] │
│   6. Conducting External Web Research ......................................... [DONE 3.1s] │
│   7. Analyzing Academic Papers & Tables ....................................... [DONE 4.2s] │
│   8. Analyzing Numerical Data with Deterministic Tools ........................ [DONE 1.1s] │
│   9. Comparing Evidence & Cross-Checking Claims ............................... [DONE 2.0s] │
│  10. Identifying Contradictions & Uncertainties ............................... [DONE 0.9s] │
│  11. Critic Review (Auditing Sufficiency & Hypotheses) ........................ [DONE 1.5s] │
│  ► 12. Synthesizing Final Intelligence Report ................................. [STREAMING] │
│                                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ 📝 Synthesizing Section 3: Comparative Degradation Rates under Industrial Composting..│  │
│  │ "According to ASTM D6400 testing in Paper [1], PLA demonstrated a 90% mass loss..."   │  │
│  └───────────────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.3 Final Report Experience & Explainability Explorer

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  SUSTAINABLE FOOD PACKAGING: 10-YEAR COMMERCIAL & TECHNICAL OUTLOOK                         │
│  Overall Confidence Score: [██████████████████░░] 82%                                       │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│  1. Executive Summary                                                                       │
│     Biodegradable polymers (primarily PLA and PHA blends) can replace up to 35% of rigid     │
│     food packaging by 2035, but barrier limitations against moisture remain a hurdle [1][3].│
│                                                                                             │
│  2. Key Findings & Evidence Matrix (Interactive Click-to-Verify)                            │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ Finding 1: PHA degradation in marine environments exceeds PLA by 4.2x [Click to View] │  │
│  │ ┌───────────────────────────────────────────────────────────────────────────────────┐ │  │
│  │ │ 🔍 EXPLAINABILITY PROVENANCE:                                                     │ │  │
│  │ │ • Claim: "PHA shows 85% biodegradation at 28 days vs 18% for PLA in seawater"   │ │  │
│  │ │ • Confidence: 0.96 (Verified by CriticAgent)                                     │ │  │
│  │ │ • Source: Journal of Applied Polymer Science (2025)                              │ │  │
│  │ │ • Location: Page 14, Table 3 (Uploaded Document: bio_marine_2025.pdf)            │ │  │
│  │ │ • Quote: "In static seawater immersion at 20°C, polyhydroxyalkanoate films..."   │ │  │
│  │ └───────────────────────────────────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                             │
│  3. Identified Contradictions & Uncertainties                                               │
│     • Paper [2] reports PLA degradation within 60 days in home compost, whereas Industrial   │
│       Standard [4] states PLA requires >58°C thermal trigger for micro-cleavage.            │
│                                                                                             │
│  4. Deterministic Data & Statistical Analysis                                               │
│     [ Interactive Chart: Cost per Kilogram Projection (2026 - 2036) ]                       │
│     *Calculated deterministically using Python SciPy statistical regression engine.         │
│                                                                                             │
│  5. Conclusions & Limitations                                                               │
│     Further lifecycle assessments are needed regarding agricultural land use for feedstock. │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.4 Research Memory Studio Layout (Phase 16)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  🧠 Research Memory Studio      [🔍 Search past concepts, findings, methodologies... ]       │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│  Filters: [ All (24) ] [ Findings (12) ] [ Hypotheses (4) ] [ Methodologies (5) ] [ Concepts] │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│  ┌──────────────────────────────────────────────────┐ ┌───────────────────────────────────┐  │
│  │ [FINDING] Degradation Rate of PLA in Seawater    │ │ [METHODOLOGY] ASTM D6400 Composting│  │
│  │ In ambient seawater (15-20°C), PLA exhibits <1.5%│ │ Standard industrial composting test│  │
│  │ degradation per year due to lack of hydrolysis.  │ │ protocol: 58°C thermophilic phase.│  │
│  │                                                  │ │                                   │  │
│  │ Confidence: [██████████████████░░] 94%           │ │ Confidence: [████████████████████] 100%│  │
│  │ Tags: #materials #marine-biodegradation #pla     │ │ Tags: #testing #standard #astm    │  │
│  │ Recalls: 3 times  •  Job: Sustainable Packaging  │ │ Recalls: 7 times  •  Job: Bio-Plastics│  │
│  └──────────────────────────────────────────────────┘ └───────────────────────────────────┘  │
│                                                                                             │
│  ┌──────────────────────────────────────────────────┐ ┌───────────────────────────────────┐  │
│  │ [HYPOTHESIS] Co-Polymerization Accelerates Rate  │ │ [CONCEPT] Enzyme-Mediated Cleavage │  │
│  │ Blending with 15% starch will lower PLA barrier. │ │ Protease K catalyzed depolymerization.│  │
│  │ Confidence: [██████████████░░░░░░] 72%           │ │ Confidence: [█████████████████░░░] 88%│  │
│  │ Tags: #formulation #hypothesis #blends           │ │ Tags: #biochem #enzymes           │  │
│  │ Recalls: 1 time   •  Job: Sustainable Packaging  │ │ Recalls: 2 times  •  Job: Polymer 2 │  │
│  └──────────────────────────────────────────────────┘ └───────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.5 Knowledge Graph Studio & Multi-Hop Pathfinder Layout (Phase 17)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  🕸️ Long-Term Knowledge Graph Studio    [ 🔍 Search Entities / Nodes... ]   [ ➕ Extract from Research ] │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  Filters: [ All Types ] [ Concepts ] [ Methods ] [ Technologies ] [ Findings ] [ Datasets ] [ Metrics ] │
├───────────────────────────────────────────────────────────────────┬─────────────────────────────────────┤
│  NETWORK VISUALIZATION CANVAS (SVG FORCE-DIRECTED LAYOUT):        │  SELECTED NODE / PATHFINDER DRAWER: │
│                                                                   │                                     │
│         (PLA Polymer) ──[accelerated_by]──► (Industrial Compost)  │  📌 Node: PLA Polymer               │
│               │                                   │               │  Type: Concept  •  Confidence: 94%  │
│          [inhibited_by]                      [produces]           │  Description: Polylactic acid       │
│               ▼                                   ▼               │  biodegradable polyester.           │
│         (Cold Seawater)                     (CO2 + Biomass)       │  Aliases: Polylactide, PLA-904      │
│               │                                                   ├─────────────────────────────────────┤
│          [measured_by]                                            │  MULTI-HOP PATHFINDER:              │
│               ▼                                                   │  From: [ PLA Polymer          ]     │
│        (ASTM D6400 Protocol)                                      │  To:   [ Cold Seawater        ]     │
│                                                                   │  [ 🚀 Find Relation Path ]          │
│  Zoom: [ 100% ] [ + ] [ - ] [ 🔄 Recenter ] [ ⛶ Fullscreen ]      │  Path Found (1 Hop):                │
│  Metrics: 42 Entities  •  88 Relations  •  0.91 Mean Confidence   │  PLA Polymer ──[inhibited_by]──►    │
│                                                                   │  Cold Seawater                      │
└───────────────────────────────────────────────────────────────────┴─────────────────────────────────────┘
```

---

### 3.7 Workspace & Projects Management Studio (Phase 18)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  🏢 BioTech Research Labs  /  📁 CRISPR Therapeutics               [ ➕ New Project ] [ 🔄 Refresh ]   │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  [ 🔍 Search projects...                     ]   [ Status: All ▾ ]                                      │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  PROJECT CARDS:                                                                                         │
│                                                                                                         │
│  ┌──────────────────────────────────────────────┐  ┌──────────────────────────────────────────────┐     │
│  │ 📁 CRISPR Therapeutics            [ ACTIVE ] │  │ 📁 mRNA Vaccine Delivery         [ ACTIVE ] │     │
│  │ Gene editing literature review and CAS9      │  │ Lipid nanoparticle carrier analysis         │     │
│  │ guide RNA optimization.                      │  │ and cellular uptake metrics.                 │     │
│  │                                              │  │                                              │     │
│  │ 🧪 8 Jobs  •  📄 24 Docs  •  🧠 12 Memories   │  │ 🧪 4 Jobs  •  📄 16 Docs  •  🧠 7 Memories   │     │
│  │ 🕸️ 38 Graph Entities                         │  │ 🕸️ 19 Graph Entities                         │     │
│  │ ──────────────────────────────────────────── │  │ ──────────────────────────────────────────── │     │
│  │ [ 🗑️ Delete ] [ 📦 Archive ]   [ ✓ SELECTED ] │  │ [ 🗑️ Delete ] [ 📦 Archive ] [ Switch Project]│     │
│  └──────────────────────────────────────────────┘  └──────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.8 Team Collaboration, Workspace Invitations & Report Review Drawer (Phase 19)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  👥 Team & Access Control: BioTech Research Labs                           [ ✖ Close ]                  │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  INVITE NEW TEAM MEMBER:                                                                                │
│  ┌───────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ [ ✉️ colleague@domain.com            ]  [ Role: Researcher ▾ ]  [ 🚀 Send Invite ]                │  │
│  └───────────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                         │
│  ACTIVE MEMBERS (3):                                                                                    │
│  ┌───────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ (AL) Alice Admin (alice@domain.com)        Joined 2026-09-10                       [ OWNER ]      │  │
│  │ (BO) Bob Analyst (bob@domain.com)          Joined 2026-09-12                       [ RESEARCHER ] │  │
│  │ (CA) Carol Reviewer (carol@domain.com)     Joined 2026-09-13                       [ REVIEWER ]   │  │
│  └───────────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                         │
│  PENDING INVITATIONS (1):                                                                               │
│  ┌───────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ ✉️ david@domain.com  •  Role: Analyst  •  Expires in 6 days    [ 📋 Copy Link ]  [ 🗑️ Revoke ]      │  │
│  └───────────────────────────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.9 Intelligent Model Ecosystem & Routing Profile Selector (Phase 20)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  ⚙️ Intelligent Model Routing Profile:                                                                   │
│  ┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐ ┌───────────────────────────────┐ │
│  │ ⚖️ Balanced        │ │ 🏆 Deep Quality    │ │ ⚡ Ultra Fast      │ │ 💰 Cost Efficient             │ │
│  │ Quality, speed, &  │ │ Frontier reasoning │ │ Low latency &      │ │ Free tier & budget-first      │ │
│  │ cost balance.      │ │ & deep synthesis.  │ │ local inference.   │ │ model allocation.             │ │
│  │   [ SELECTED ]     │ │                    │ │                    │ │                               │ │
│  └────────────────────┘ └────────────────────┘ └────────────────────┘ └───────────────────────────────┘ │
│                                                                                                         │
│  ℹ️ Routing Target: gemini-2.5-pro (gemini)  [ Pareto Optimal ]  •  Quality: 0.95 | Speed: 0.70 | Cost: Free│
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

---

### 3.10 Model Evaluation & Benchmark Leaderboard Studio (Phase 21)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  🏆 Model Benchmark Leaderboard                       [ 🔄 Refresh ]  [ ▶️ Run Benchmark ]              │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  ACTIVE MODEL RANKINGS:                                                                                 │
│  ┌──────┬─────────────────────┬───────────────┬────────────┬───────────┬───────────┬──────────────┐    │
│  │ RANK │ MODEL               │ OVERALL SCORE │ FACTUALITY │ REASONING │ LATENCY   │ STATUS       │    │
│  ├──────┼─────────────────────┼───────────────┼────────────┼───────────┼───────────┼──────────────┤    │
│  │  🥇1 │ gemini-2.0-flash    │ ████████ 89%  │ 94.0%      │ 88.5%     │ 320 ms    │ [ ⚡ Pareto ] │    │
│  │  🥈2 │ gemini-1.5-pro      │ ███████  86%  │ 92.0%      │ 91.0%     │ 650 ms    │ [ Standard ] │    │
│  │  🥉3 │ gpt-4o-mini         │ ███████  84%  │ 89.0%      │ 85.0%     │ 410 ms    │ [ Standard ] │    │
│  │   4  │ llama3:8b (Ollama)  │ █████    68%  │ 72.0%      │ 65.0%     │ 180 ms    │ [ ⚡ Pareto ] │    │
│  └──────┴─────────────────────┴───────────────┴────────────┴───────────┴───────────┴──────────────┘    │
│                                                                                                         │
│  RECENT BENCHMARK RUNS (Click to inspect test cases):                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────────┬─────────────────────┐ │
│  │ 🔍 gemini-2.0-flash  •  2026-09-13 15:30  •  5 Samples • Pass Rate: 100%   │ Score: 89.2%    [ > ] │ │
│  │ 🔍 llama3:8b         •  2026-09-13 14:15  •  5 Samples • Pass Rate: 80%    │ Score: 68.0%    [ > ] │ │
│  └─────────────────────────────────────────────────────────────────────────────┴─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.11 Agent Observability & Evaluation Studio (Phase 22)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  ⚡ Agent Observability Studio                         [ 🔄 Refresh ]  [ ▶️ Evaluate Agent ]            │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  SYSTEM-WIDE METRICS SUMMARY:                                                                           │
│  ┌──────────────────┬──────────────────┬──────────────────┬──────────────────┬───────────────────────┐  │
│  │ Overall Quality  │ Plan Precision   │ Tool Accuracy    │ Grounded Coverage│ Hallucination Rate    │  │
│  │     94.2%        │     92.5%        │     98.0%        │      91.4%       │        2.8%           │  │
│  └──────────────────┴──────────────────┴──────────────────┴──────────────────┴───────────────────────┘  │
│                                                                                                         │
│  SPECIALIZED AGENT ARCHITECTURE HEALTH:                                                                 │
│  ┌────────────────────┬────────────────────┬────────────────────┬────────────────────┬───────────────┐  │
│  │ PlannerAgent       │ WebResearchAgent   │ DocumentReaderAgent│ CriticAgent        │ ReportAgent   │  │
│  │ [ 🟢 Active ]      │ [ 🟢 Active ]      │ [ 🟢 Active ]      │ [ 🟢 Active ]      │ [ 🟢 Active ] │  │
│  └────────────────────┴────────────────────┴────────────────────┴────────────────────┴───────────────┘  │
│                                                                                                         │
│  AGENT EVALUATION RUNS (Click to inspect step telemetry & hallucinations):                              │
│  ┌─────────────────────────────────────────────────────────────────────────────┬─────────────────────┐  │
│  │ ⚡ ResearchPipeline  •  12 Steps • 100% Tools • 0.0% Hallucination         │ Score: 96.5%    [ > ] │  │
│  │ ⚡ WebResearchAgent  •   6 Steps • 100% Tools • 3.2% Hallucination         │ Score: 92.0%    [ > ] │  │
│  └─────────────────────────────────────────────────────────────────────────────┴─────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.12 Enterprise Security, KMS Secret Vault & Compliance Studio (Phase 23)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  🛡️ Enterprise Security & Compliance Studio           [ 🔄 Refresh ]  [ 🔒 Verify Audit Chain ]         │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  [ 🛡️ Compliance Status ]  [ 🔑 KMS Secret Vault ]  [ 📜 Immutable Audit Logs ]  [ ⏳ Retention & GDPR ] │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  COMPLIANCE SCORECARD OVERVIEW:                                                                         │
│  ┌──────────────────────────────────────────────┐  ┌──────────────────────────────────────────────┐     │
│  │ 🛡️ SOC 2 Type II Compliance       [ ACTIVE ] │  │ ⚖️ GDPR Data Privacy             [ ACTIVE ] │     │
│  │ • CC6.1 Access Control: RBAC Enforced        │  │ • Article 17: Right-to-be-Forgotten Ready   │     │
│  │ • CC6.6 Encryption: AES-256-GCM Envelope     │  │ • Article 25: Tenant Isolation & Anonymize   │     │
│  │ • CC7.2 Audit Trail: Merkle Hash Chained     │  │ • Article 32: KMS Wrapped Security           │     │
│  │ Status: 🟢 COMPLIANT                         │  │ Status: 🟢 COMPLIANT                         │     │
│  └──────────────────────────────────────────────┘  └──────────────────────────────────────────────┘     │
│                                                                                                         │
│  KMS ENCRYPTED SECRETS VAULT:                                                                           │
│  ┌────────────────────────────────┬────────────┬──────────────┬──────────────────┬───────────────────┐  │
│  │ SECRET NAME                    │ PROVIDER   │ TYPE         │ MASKED PREVIEW   │ ACTIONS           │  │
│  ├────────────────────────────────┼────────────┼──────────────┼──────────────────┼───────────────────┤  │
│  │ Production Gemini API Key      │ Gemini     │ API Key      │ `AIz...8877`     │ [ 🚫 Revoke ] [ 🗑]│  │
│  │ Enterprise Anthropic Key       │ Anthropic  │ API Key      │ `sk-...1122`     │ [ 🚫 Revoke ] [ 🗑]│  │
│  └────────────────────────────────┴────────────┴──────────────┴──────────────────┴───────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.13 Production Infrastructure & Cluster Topology Studio (Phase 24)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  ⚡ Production Infrastructure & Cluster Studio    [ 🔄 Refresh ] [ 💓 Pulse Heartbeat ] [ ➕ Enqueue ]    │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  [ 🖥️ Cluster Topology ]    [ 📥 Distributed Task Queue ]    [ 🗄️ S3/MinIO Blob Vault ]                 │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  CLUSTER HEALTH & AGGREGATE LOAD:                                                                       │
│  ┌─────────────────────────┬─────────────────────────┬─────────────────────────┬─────────────────────┐  │
│  │ Total Cluster Nodes: 4  │ Active Executions: 6    │ Queue Backlog: 2 Tasks  │ Storage: 418.2 MB   │  │
│  └─────────────────────────┴─────────────────────────┴─────────────────────────┴─────────────────────┘  │
│                                                                                                         │
│  WORKER INSTANCES:                                                                                      │
│  ┌────────────────────────────┬───────────┬──────────────┬──────────────────────────┬────────────────┐  │
│  │ NODE ID / HOST             │ STATUS    │ CPU / RAM    │ CAPABILITIES             │ ACTIONS        │  │
│  ├────────────────────────────┼───────────┼──────────────┼──────────────────────────┼────────────────┤  │
│  │ 🟢 worker-alpha (k8s-node1) │ ready     │ 24% / 48%    │ `web_search`, `pdf_parse`│ [ 🛑 Drain ]   │  │
│  │ 🟢 worker-beta (k8s-node2)  │ busy      │ 78% / 62%    │ `multimodal`, `vision`   │ [ 🛑 Drain ]   │  │
│  └────────────────────────────┴───────────┴──────────────┴──────────────────────────┴────────────────┘  │
│                                                                                                         │
│  UNIFIED S3/MINIO OBJECT BLOB VAULT:                                                                    │
│  ┌─────────────────────────────┬───────────┬──────────────┬───────────────┬──────────────────────────┐  │
│  │ OBJECT KEY                  │ BUCKET    │ SIZE         │ CONTENT TYPE  │ ACTIONS                  │  │
│  ├─────────────────────────────┼───────────┼──────────────┼───────────────┼──────────────────────────┤  │
│  │ `reports/job_401_final.pdf` │ artifacts │ 4.82 MB      │ `app/pdf`     │ [ 🔗 Presigned URL ] [ 🗑]│  │
│  │ `datasets/market_2026.csv`  │ datasets  │ 142.50 MB    │ `text/csv`    │ [ 🔗 Presigned URL ] [ 🗑]│  │
│  └─────────────────────────────┴───────────┴──────────────┴───────────────┴──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.14 Developer Platform & API Playground Studio (Phase 25)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  💻 Developer Platform & Public API                     [ 🔄 Refresh ] [ ➕ Create API Key ]            │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  [ 🔑 API Keys (3) ]       [ 💻 API Playground & SDK ]       [ ⚡ Rate Limits & Quotas ]                 │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  API KEYS VAULT:                                                                                        │
│  ┌──────────────────────────────┬─────────────────────┬────────────┬──────────────┬──────────────────┐  │
│  │ KEY NAME                     │ MASKED KEY          │ TIER       │ STATUS       │ ACTIONS          │  │
│  ├──────────────────────────────┼─────────────────────┼────────────┼──────────────┼──────────────────┤  │
│  │ Production Automation Bot    │ `amrp_live_...9f8a` │ Enterprise │ 🟢 Active    │ [ 🚫 Revoke ] [🗑]│  │
│  │ Development Local Test       │ `amrp_live_...3b21` │ Free       │ 🟢 Active    │ [ 🚫 Revoke ] [🗑]│  │
│  └──────────────────────────────┴─────────────────────┴────────────┴──────────────┴──────────────────┘  │
│                                                                                                         │
│  INTERACTIVE SDK CODE GENERATOR (POST /api/v1/developer/research):                                      │
│  [ cURL ]  [ Python (requests) ]  [ TypeScript (Axios) ]                         [ 📋 Copy Snippet ]    │
│  ┌───────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ import requests                                                                                   │  │
│  │ response = requests.post(                                                                         │  │
│  │     "https://api.research-os.ai/api/v1/developer/research",                                       │  │
│  │     headers={"X-API-Key": "amrp_live_your_api_key_here"},                                        │  │
│  │     json={"question": "What are the latest breakthroughs in high-temperature superconductors?"}   │  │
│  │ )                                                                                                 │  │
│  │ print(response.json())                                                                            │  │
│  └───────────────────────────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 3.15 Research Automation & Scheduled Sweeps Studio (Phase 26)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  📡 Research Automation & Scheduled Sweeps              [ 🔄 Refresh ] [ ➕ Create Schedule ]           │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  [ ⏰ Sweeps & Schedules (3) ]   [ 📜 Sweep History & Diff Explorer ]   [ 🔔 Dispatched Alerts (4) ]     │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  SCHEDULED TOPIC SWEEPS:                                                                                │
│  ┌─────────────────────────────────────┬───────────────────┬───────────────┬─────────────────────────┐  │
│  │ SCHEDULE TITLE                      │ FREQUENCY / CRON  │ NOVELTY THRESH│ ACTIONS                 │  │
│  ├─────────────────────────────────────┼───────────────────┼───────────────┼─────────────────────────┤  │
│  │ Quantum Computing Quantum Supremacy │ Every 24 hours    │ 0.35 (Medium) │ [⚡ Run Now] [⏸] [🗑]   │  │
│  │ Solid-State Battery Breakthroughs   │ `0 9 * * 1` (Mon) │ 0.40 (High)   │ [⚡ Run Now] [⏸] [🗑]   │  │
│  └─────────────────────────────────────┴───────────────────┴───────────────┴─────────────────────────┘  │
│                                                                                                         │
│  SEMANTIC DIFF & NOVELTY EXPLORER:                                                                      │
│  ┌───────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ Sweep: Solid-State Battery (Executed 10 mins ago) — Novelty Score: 0.72 [HIGH NOVELTY]             │  │
│  │ 🟢 Novel Claim: "Solid-state electrolyte achieves 98% retention after 1,500 fast-charge cycles."   │  │
│  │ 🔴 Contradiction: "Rebuts 2024 assumption of severe dendritic degradation at >4C charging rate."  │  │
│  │ 🔗 Sources Crawled: arXiv:2609.04112, nature.com/articles/s41586-026-0012                        │  │
│  └───────────────────────────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. UI Interaction States

| State | Visual Treatment | Transition |
|---|---|---|
| **Formulation** | Focused search bar with glowing cyan border and toggle pill filters (Web, Knowledge, Data) | Smooth expand on focus |
| **Stream Processing** | Pulsing emerald step nodes, animated progress bars, live markdown token streaming | WebSocket event triggered |
| **Evidence Hover** | Elevation increase, amber badge for contradictions, green badge for high confidence | 150ms ease-out hover |
| **Explainability Modal** | Glassmorphic slide-out drawer revealing exact document slice and table coordinates | Slide-left 250ms |
| **Report Review Drawer** | Slide-over drawer on synthesized report view with section quotes, comment threads, filter tabs (All, Open, Resolved), and 1-click resolution | Slide-left 200ms ease-out |
| **Routing Profile Selector** | Interactive 4-card grid with active border glow, icon badge, and live Pareto-optimal simulation pill | Instant selection & async fetch |
| **Model Leaderboard Studio** | Ranked tabular scoreboard with score meters, Pareto badges, and test case audit drawer | Instant click / modal slide |
| **Agent Observability Studio** | KPI metrics cards, per-agent health indicators, evaluation scorecards, and sequential step telemetry inspector drawer | Instant click / slide drawer |
| **Enterprise Security Studio** | Tabbed compliance cards, KMS secret creation modal, SHA-256 hash-anchored log explorer, and confirmation-gated GDPR purge modal | Instant tab switch / animated drawer |
| **Production Infrastructure Studio** | Tabbed cluster topology, live CPU/RAM load bars, heartbeat pulse simulator, priority task enqueue modal, and S3 presigned URL generator | Instant tab switch / modal overlay |
| **Developer Platform Studio** | Tabbed API key management, one-time plaintext key reveal modal, interactive code snippets (cURL/Python/TS), and tier rate limit cards | Instant tab switch / modal overlay |
| **Research Automation Studio** | Tabbed cron sweeps, countdown badges, diff explorer with novel/contradictory highlight tags, novelty gauge, and alert cards | Instant tab switch / modal overlay |
| **Memory Exploration** | Filter chips for finding/hypothesis/methodology, confidence bar, tag search | Instant client-side filter / API query |
| **Error / Fallback** | Subtle amber notice indicating automatic failover to fallback model provider | Non-blocking toast notification |

