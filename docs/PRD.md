# Product Requirements Document (PRD)

## Project: Agentic Multimodal Research Platform (AI Research OS)
**Status**: Active / Production v1.1 (All 34 Phases Complete across Generations 1-8)  
**Author**: Engineering & AI Systems Team  
**Last Updated**: September 2026  
**Stable Branch**: `develop/v1.1`

---

## 1. Executive Summary & Vision

The **Agentic Multimodal Research Platform** is an enterprise-grade, local-first **AI Research Operating System**. It transforms ambiguous, complex research inquiries into structured, verified, and citation-backed intelligence reports with complete auditability, zero hallucinations, and strict data privacy.

### The Core Paradigm Shift
> **This isn't just a chatbot.**  
> Rather than a single prompt `Question $\rightarrow$ LLM $\rightarrow$ Answer`, the system executes an autonomous agentic pipeline:  
> **Plan $\rightarrow$ Investigate $\rightarrow$ Retrieve $\rightarrow$ Reason $\rightarrow$ Critique $\rightarrow$ Synthesize $\rightarrow$ Report**, while managing multi-user authentication, quota allocation, multi-provider model routing, persistent storage, and real-time streaming progress.

---

## 2. Problem Statement

Modern intelligence gathering, academic research, and technical analysis face four critical bottlenecks:
1. **Multimodal Data Fragmentation**: Information is trapped across disconnected sources—academic PDFs with embedded tables, scanned diagrams, intranet DOCX files, spreadsheets, and dynamic web pages.
2. **Hallucinations & Lack of Provenance**: Standard LLMs generate authoritative-sounding answers without verifiable source citations, page-level anchors, or confidence scoring.
3. **Monolithic Task Limits**: Complex research queries require strategic decomposition, parallel sub-investigations, iterative verification, and synthesis—capabilities that single-prompt models cannot achieve.
4. **Cloud Privacy & Vendor Lock-In**: Organizations hesitate to upload sensitive proprietary research to closed commercial AI clouds.

---

## 3. Target Users & Personas

- **Enterprise Researchers & Analysts**: Need deep literature synthesis across hundreds of pages of internal and external documentation with strict evidence mapping.
- **R&D Engineers & Scientists**: Require precise technical summaries with exact data extraction from PDF tables, mathematical formulas, and scientific preprints.
- **Academics & Graduate Students**: Require literature reviews comparing methodologies, identifying contradictions across papers, and generating verifiable citations.
- **Compliance & Legal Officers**: Require 100% provenance and citation tracking for every factual claim.
- **Self-Hosted / Privacy-Conscious Organizations**: Need the entire agentic pipeline to run offline or local-first using local hardware (Ollama) without data leakage.

---

## 4. Business & Quota Model

The platform includes persistent usage tracking and token/cost quota enforcement with three distinct service tiers:

| Tier | Research Jobs | Token / Cost Quotas | Knowledge Storage | Model Access | Collaboration |
|---|---|---|---|---|---|
| **FREE** | Limited concurrent jobs | Strict lifetime/monthly token limits | Limited document storage | Local / Standard Fast Models | Single User |
| **PRO** | High concurrent jobs | Expanded token & cost quotas | Large private knowledge base | Advanced Reasoning & Vision Models | Single User |
| **TEAM** | Unlimited concurrent jobs | Shared team quotas & cost centers | Shared organizational knowledge | All Catalog & Custom Models | Shared Workspaces, Roles & Versioning |

---

## 5. End-to-End User Experience

### 5.1 Platform Navigation & Dashboard
The UI provides a unified research workspace:
- **Dashboard**: Recent research jobs, execution states, quick research launcher.
- **Research**: Active investigations, live DAG visualization, real-time WebSocket logs.
- **Knowledge**: Private knowledge base, indexed document collections, chunk statistics.
- **Documents**: Upload hub for PDFs, DOCX, images, datasets (CSV, Excel).
- **Projects & Workspaces**: Structured project folders and team spaces (Generation 4).
- **Reports**: Finished intelligence reports with citation explorer and export options.
- **Memory**: Persistent cross-session research memory studio, conceptual indexing, tag filters.
- **Settings**: Model provider toggles, Ollama endpoints, API keys, quota monitors.

### 5.2 Research Execution Progression
When a user submits a query (e.g., *"Analyze whether biodegradable packaging can realistically replace conventional plastic in food packaging over the next 10 years"*), the system streams progress in real time:
1. `Understanding Request...`
2. `Recalling Cross-Session Research Memory...`
3. `Planning Research & Decomposing Subquestions...`
4. `Checking Private Knowledge Base...`
5. `Retrieving Relevant Document Context...`
6. `Conducting External Web Investigations...`
7. `Analyzing Academic Papers & Tables...`
8. `Analyzing Tabular Data & Statistics...`
9. `Comparing Evidence & Cross-Checking Claims...`
10. `Identifying Contradictions & Uncertainties...`
11. `Critic Review (Auditing Sufficiency & Hypothesis Testing)...`
12. `Iterative Deep Research Loop (if evidence gaps or hypotheses unverified)...`
13. `Synthesizing Final Intelligence Report...`
14. `Auto-Persisting Verified Findings to Research Memory...`
15. `Completed & Ready for Interactive Exploration.`

### 5.3 Final Report Experience & Explainability
The output is a structured intelligence dossier:
- **Executive Summary**: High-level overview of findings.
- **Research Question & Scope**: Precise parameters of the investigation.
- **Methodology**: Strategy, data sources queried, and agent workflows.
- **Key Findings**: Numbered, authoritative findings.
- **Evidence Matrix**: Detailed breakdown mapping every claim to exact sources (e.g., `Paper A - Page 12`, `Uploaded Doc B - Section 4.2`, `Web Source C`).
- **Contradictions & Uncertainty Analysis**: Explicit identification of conflicting data across sources.
- **Market & Technical Analysis**: In-depth evaluation of technological and economic viability.
- **Data Analysis & Visualizations**: Deterministically calculated statistics, tables, and charts.
- **Risks & Limitations**: Known unknowns, study limitations, and external risks.
- **Conclusion**: Actionable synthesis.
- **Confidence / Evidence Coverage Score**: Quantitative coverage metric (e.g., `82% Confidence`).
- **Explainability Anchor ("Why do you believe this?")**: Interactive provenance lookup:  
  `Answer $\rightarrow$ Reasoning/Evidence $\rightarrow$ Sources $\rightarrow$ Original Documents $\rightarrow$ Relevant Pages/Sections`.

---

## 6. Current Completed Scope (Phases 1 – 34)

- ✅ **Phases 1 – 26 (Generations 1 – 6)**: Core monorepo structure, DAG orchestration, multimodal ingestion (PDF, DOCX, datasets, audio, video), Hybrid RRF RAG, ModelGateway with row-locking quotas, Deep Research engine, Research Memory, Knowledge Graph, Workspaces, Collaboration, Model & Agent Evaluation, Enterprise Security, Infrastructure, Developer Platform, and Research Automation.
- ✅ **Phase 27 (Adversarial Multi-Agent Debate Engine)**: Multi-agent dialectical debate studio (`ProposerAgent` vs `OpposerAgent`), dynamic Elo rating shifts, impartial arbitration, and consensus synthesis.
- ✅ **Phase 28 (Systematic Literature Review & Meta-Analysis Engine)**: PRISMA 2020 four-stage study flow tracking, Cochrane Risk of Bias (RoB 2) quality scoring, and quantitative meta-analysis statistical pooling (Forest plots, Cohen's $d$, Hedges' $g$, $I^2$ index).
- ✅ **Phase 29 (In-Silico Experimentation & Computational Reproducibility)**: AST-sandboxed code execution, empirical claim verification traces, and replication tolerance delta scoring.
- ✅ **Phase 30 (Multimodal Scientific Presentation & Executive Podcasting)**: 16:9 structured slide deck generator and multi-speaker executive podcast audio dialogue synthesizer.
- ✅ **Phase 31 (Autonomous Peer Review & Academic Journal Publishing)**: Double-blind referee panels, author rebuttals, and camera-ready LaTeX/BibTeX preprint generation.
- ✅ **Phase 32 (Real-Time Collaborative Research Canvas & Visual Ideation)**: Infinite 2D spatial canvas, node-link visual DAGs, and AI brainstorming nodes.
- ✅ **Phase 33 (Synthetic Instruction Dataset Generation & Active Learning Engine)**: Evol-Instruct prompt mutators, Alpaca/ShareGPT/DPO/CoT format adapters, and active learning curation studio.
- ✅ **Phase 34 (Autonomous Patent Landscape Analysis & Prior Art Search Engine)**: 35 U.S.C. 102/103 prior art claim charts, FTO clearance gauge, and white-space patentability opportunity discovery.

---

## 7. 8-Generation Product Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                   AGENTIC MULTIMODAL RESEARCH PLATFORM ROADMAP                   │
└──────────────────────────────────────────────────────────────────────────────────┘
  Phases 1 - 14: Core Foundations, Multimodal Intelligence & Paper Analysis [COMPLETE]
                             │
                             ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │ GENERATION 3: Autonomous Research                                            │
  │ • Phase 15: Deep Research Engine (Recursive Feedback Loops) [COMPLETE]       │
  │ • Phase 16: Research Memory (Cross-Session Project Memory)  [COMPLETE]       │
  │ • Phase 17: Long-Term Knowledge Graph (Entity-Relation Reasoning) [COMPLETE] │
  └──────────────────────────────────────┬───────────────────────────────────────┘
                                         ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │ GENERATION 4: Collaboration Platform                                         │
  │ • Phase 18: Projects & Workspaces Organization [COMPLETE]                    │
  │ • Phase 19: Team Collaboration (Roles, Invites, Report Annotations) [COMPLETE]│
  └──────────────────────────────────────┬───────────────────────────────────────┘
                                         ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │ GENERATION 5: AI Platform Intelligence                                       │
  │ • Phase 20: Intelligent Model Ecosystem (Pareto Frontier Routing) [COMPLETE] │
  │ • Phase 21: Model Evaluation System (Automated Benchmarking) [COMPLETE]      │
  │ • Phase 22: Agent Evaluation (Hallucination & Efficiency) [COMPLETE]         │
  └──────────────────────────────────────┬───────────────────────────────────────┘
                                         ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │ GENERATION 6: Production Product                                             │
  │ • Phase 23: Enterprise Security (SOC 2, GDPR, Immutable Audit Logs) [COMPLETE]│
  │ • Phase 24: Production Scale Infrastructure (Task Queues, Blob Vault) [COMPLETE]
  │ • Phase 25: Public API & Developer Platform (SDKs, API Keys) [COMPLETE]      │
  │ • Phase 26: Research Automation (Scheduled Sweeps, Alerting) [COMPLETE]      │
  └──────────────────────────────────────┬───────────────────────────────────────┘
                                         ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │ GENERATION 7: Scientific & Meta-Intelligence                                 │
  │ • Phase 27: Adversarial Multi-Agent Debate & Consensus Engine [COMPLETE]     │
  │ • Phase 28: Systematic Literature Review & PRISMA Meta-Analysis [COMPLETE]   │
  │ • Phase 29: In-Silico Reproducibility & Sandbox Verification [COMPLETE]      │
  │ • Phase 30: Multimodal Presentation Studio & Podcast Synthesizer [COMPLETE]  │
  └──────────────────────────────────────┬───────────────────────────────────────┘
                                         ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │ GENERATION 8: Autonomous Meta-Science & Publishing Ecosystem                 │
  │ • Phase 31: Autonomous Peer Review & Journal Publishing Pipeline [COMPLETE]  │
  │ • Phase 32: Real-Time Collaborative Research Canvas Studio [COMPLETE]        │
  │ • Phase 33: Synthetic Instruction Dataset Gen & Active Learning [COMPLETE]   │
  │ • Phase 34: Autonomous Patent Landscape Analysis & Prior Art Search [COMPLETE]│
  │ • Phase 35: Autonomous Scientific Grant & Funding Proposal Studio [COMPLETE] │
  └──────────────────────────────────────┬───────────────────────────────────────┘
                                         ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │ GENERATION 10: Clinical Intelligence & Developer Platform Ecosystem          │
  │ • Phase 36: Autonomous Clinical Trial Protocol & Drug Repurposing [COMPLETE] │
  │ • Official Developer Platform SDKs (Python async + TypeScript) [COMPLETE]    │
  │ • Production Demo Data Seeder (Cross-Studio Full Platform Seed) [COMPLETE]   │
  └──────────────────────────────────────┬───────────────────────────────────────┘
                                         ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │ GENERATION 11: Laboratory Automation & Cloud Biofoundry Integration          │
  │ • Phase 37: Autonomous Robotic Protocol Generator & Deck Simulation [COMPLETE]│
  └──────────────────────────────────────┬───────────────────────────────────────┘
                                         ▼
                            [ AI RESEARCH OPERATING SYSTEM ]
```

---

## 8. Architectural Anti-Patterns ("What We Should NOT Do")

To maintain momentum and high engineering quality, the following anti-patterns are strictly avoided:
1. **No Premature Infrastructure Bloat**: Do NOT introduce Kafka, Kubernetes distributed workers, 10 LLM providers, OAuth microservices, or redundant vector databases before the core agentic research loops are connected and useful.
2. **No Monolithic LLM Prompts**: Never replace multi-agent DAG decomposition with a single massive LLM prompt.
3. **No Hallucinated Calculations**: Never ask LLMs to perform arithmetic or statistical calculations directly; always delegate to deterministic tools.
4. **Core Philosophy**: **Make the research engine excellent first $\rightarrow$ make knowledge deeply integrated $\rightarrow$ make evidence trustworthy $\rightarrow$ make multimodal analysis powerful $\rightarrow$ make it collaborative $\rightarrow$ make it production-grade.**
