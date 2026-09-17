# Agentic Multimodal Research Platform (AI Research OS)

<p align="left">
  <a href="https://github.com/Om-Talaviya"><img src="https://img.shields.io/badge/Architect-Om%20Talaviya-38bdf8?style=flat-square&logo=github&logoColor=white" alt="Author" /></a>
  <img src="https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776ab?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Framework-FastAPI%20%26%20LangGraph-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Modality-Multimodal%20RAG%20%26%20Multi--Omics-7c3aed?style=flat-square" alt="Multimodal" />
  <img src="https://img.shields.io/badge/Status-Phase%2082%20Complete%20(v1.1%20Release)-success?style=flat-square" alt="Status" />
  <img src="https://img.shields.io/badge/Tests-540+%20Passing%20(100%25%20CI)-brightgreen?style=flat-square" alt="Tests" />
  <img src="https://img.shields.io/badge/SDKs-Python%20%26%20TypeScript-blueviolet?style=flat-square" alt="SDKs" />
  <img src="https://img.shields.io/badge/Branch-develop%2Fv1.1-blue?style=flat-square" alt="Branch" />
</p>

An enterprise-grade, local-first **AI Research Operating System (Research OS v1.1)** that conducts autonomous, verifiable, and evidence-grounded investigations across scientific literature, multi-omics biological data, molecular structures, laboratory robotics, clinical protocols, and physical simulations.

> **This is an AI Scientist, Not Just a Chatbot.**  
> The platform autonomously orchestrates **Hypothesis Formation $\rightarrow$ Literature Mining $\rightarrow$ Computational In-Silico Modeling $\rightarrow$ Empirical Verification $\rightarrow$ Peer Review $\rightarrow$ Publication $\rightarrow$ Wet-Lab Protocol Translation**, backed by persistent multi-tenant security, transactional quotas, multi-model fallback gateways, and real-time WebSocket streaming.

---

## 🏗️ High-Level System Architecture

```
                                  ┌──────────────┐
                                  │  RESEARCHER  │
                                  └───────┬──────┘
                                          │
                                          ▼
                        ┌─────────────────────────────────┐
                        │      React 18 Web Platform      │
                        │ (82 Specialized Research Hubs)  │
                        └────────────────┬────────────────┘
                                          │ HTTP / WebSocket
                                          ▼
                        ┌─────────────────────────────────┐
                        │       FastAPI Gateway           │
                        │   (82 Domain REST Routers)      │
                        └────────┬───────────────┬────────┘
                                  │               │
                  ┌───────────────┘               └───────────────┐
                  ▼                                               ▼
       ┌─────────────────────┐                         ┌─────────────────────┐
       │   Research Engine   │                         │   Knowledge Layer   │
       │ (Agent Orchestrator)│                         │ (Hybrid RAG & Super)│
       └──────────┬──────────┘                         └──────────┬──────────┘
                  │                                               │
         ┌────────┴───────────────────┐                           │
         ▼              ▼             ▼                           │
    ┌─────────┐   ┌───────────┐ ┌──────────┐                      │
    │ Planner │   │ Web Agent │ │Doc Agent │                      │
    └────┬────┘   └─────┬─────┘ └────┬─────┘                      │
         │              │            │                            │
         └──────────────┼────────────┴────────────────────────────┤
                        ▼                                         │
                  ┌───────────┐                                   │
                  │  Critic   │◄──────────────────────────────────┘
                  └─────┬─────┘
                        ▼
                  ┌───────────┐
                  │ Synthesis │
                  └─────┬─────┘
                        ▼
                  ┌───────────┐
                  │  Report   │
                  └───────────┘

 ═════════════════════════════════════════════════════════════════════════════════
                                PLATFORM INFRASTRUCTURE
 ─────────────────────────────────────────────────────────────────────────────────
   [Security & Auth]      [AI Orchestration]              [Platform Persistence]
   • PBKDF2 & JWT Auth    • ModelRegistry (Capabilities)   • PostgreSQL 16 / SQLite
   • AES-256 KMS Vault    • Pareto Router (Cost/Speed/Acc) • ChromaDB Vector Store
   • Merkle Audit Chains  • Multi-Model Fallback Gateway   • Knowledge Super-Graph
   • GDPR Article 17 Purge• Ollama / Gemini / OpenAI / Anth• Parquet / Iceberg Lake
 ═════════════════════════════════════════════════════════════════════════════════
```

---

## ⚡ What Makes This Platform Different?

| Dimension | Generic LLM Chatbot / Wrapper | Agentic Multimodal Research Platform (v1.1) |
|---|---|---|
| **Execution Paradigm** | Single prompt $\rightarrow$ single speculative reply | Multi-agent DAG execution: `Plan $\rightarrow$ Retrieve $\rightarrow$ Model $\rightarrow$ Critique $\rightarrow$ Re-evaluate $\rightarrow$ Synthesize` |
| **Model Coupling** | Single vendor lock-in | **Model-Agnostic Pareto Gateway**: Dynamically matches fast, vision, or deep reasoning models with instant zero-downtime failover |
| **Scientific Evidence** | Unverified claims and hallucinations | **Strict Claim $\rightarrow$ Evidence Matrix**: Explicit anchoring to literature DOIs, clinical trial IDs, UniProt accession, and PDB coordinates |
| **Verification Loop** | No verification mechanism | Independent `CriticAgent` detects mathematical contradictions, audits citation sufficiency, and triggers iterative replanning |
| **Dialectical Debate** | Monolithic agreement / echo chamber | `ProposerAgent` vs `OpposerAgent` dialectics with Elo ratings and impartial consensus arbitration |
| **Multi-Omics & Biology** | Text-only approximations | Native engines for scRNA-seq, CRISPR Cas9/12a/13, ATAC-seq, spatial transcriptomics, neoepitopes, and CAR-T cell therapy |
| **Molecular Modeling** | Static strings | AlphaFold3/ESMFold 3D structures, AutoDock Vina ligand docking, all-atom Velocity Verlet MD, DFT quantum bandgaps, and smFRET |
| **Laboratory Translation**| Theoretical suggestions | Compiles verified in-silico findings into runnable robotic automation protocols (Opentrons Python API v2, PyLabRobot) |
| **Regulatory & Clinical** | Generic advice | 21 CFR Part 11 electronic audit trails, eCTD FDA IND / EMA CTD dossiers, ACMG variant scoring, and FAERS signal mining |
| **Data Lakehouse** | Session storage | Parquet/Iceberg scientific data lakehouse with duckdb SQL and vector embeddings across petabyte-scale datasets |

---

## 🚀 Complete 82-Phase Engineering Matrix

The platform is organized into **6 Grand Research Domains** comprising 82 fully implemented, tested, and integrated phases:

### 1. Autonomous Cognition, Literature & Meta-Science
* **Phases 1–11**: Core Research Engine, Hierarchical Query Planning, Web & Multimodal Document Ingestion, and Citation Anchoring.
* **Phase 15**: Recursive Deep Research Engine with Dynamic Hypothesis Branching.
* **Phase 27**: Adversarial Multi-Agent Debate Arena with Elo Consensus Arbitration.
* **Phase 28**: Systematic Literature Reviews with PRISMA 2020 Flow Tracking and Meta-Analysis Forest Plots.
* **Phase 29**: In-Silico Computational Code Execution & Statistical Reproducibility Verifier.
* **Phase 30**: Multimodal 16:9 Scientific Presentation and Executive Podcast Briefing Generator.
* **Phase 31**: Autonomous Double-Blind Peer Review Simulator and Camera-Ready LaTeX Preprint Publisher.
* **Phase 33**: Evolutionary Active Learning & Synthetic Instruction Dataset Synthesizer (Alpaca/ShareGPT/DPO).
* **Phase 35**: Multi-Year NIH/NSF Scientific Grant Proposal Synthesizer with Institutional Budgeting.
* **Phase 50**: Autonomous AI Scientist Self-Evolving Discovery Engine.
* **Phase 51**: RAGAS Groundedness Evaluation and Adversarial Red-Teaming Gateway.

### 2. Genomics, Epigenomics & Synthetic Biology
* **Phase 40**: Synthetic Biology & CRISPR-Cas9/Cas12a Guide RNA Designer with Off-Target CFD Scoring.
* **Phase 41**: Single-Cell Transcriptomics (scRNA-seq) Differential Expression Studio (Scanpy/AnnData).
* **Phase 55**: Computational Immunology & TCR-pMHC Neoantigen Binding Predictor.
* **Phase 56**: Epigenomic Chromatin Accessibility & ATAC-seq Peak Calling Engine.
* **Phase 65**: Synthetic Biology DNA Logic Gate & Toggle Switch Circuit Compiler (SBOL3).
* **Phase 67**: Proteogenomic Neoepitope Discovery & Personalized Cancer Vaccine Designer.
* **Phase 70**: Target Validation & CRISPR Synthetic Lethality Matrix (DepMap CERES/Chronos).
* **Phase 72**: Synthetic Gene Circuit Stability & Host Metabolic Burden Forecaster.
* **Phase 74**: Genomic Variant Pathogenicity & ACMG/AMP 2015 28-Criteria Classification Engine.
* **Phase 82**: Metagenomic Pathogen Surveillance & Antimicrobial Resistance (AMR) CARD Resistome Engine.

### 3. Structural Biology, Chemistry & Biophysics
* **Phase 38**: AlphaFold3 & ESMFold Bio-Molecular 3D Structure Visualizer and pLDDT Spectrum Analyzer.
* **Phase 39**: All-Atom Velocity Verlet Molecular Dynamics Trajectory and Quantum DFT Bandgap Studio.
* **Phase 43**: De Novo Generative Chemistry & Antibody Design Studio (Diffusion & VAE).
* **Phase 44**: Scientific Knowledge Super-Graph & Cross-Domain Hypothesis Discovery Engine.
* **Phase 45**: Drug Repurposing & Multi-Target Synergy Matrix (Bliss/Loewe Additivity).
* **Phase 47**: Cryo-EM Density Map Fitting & Macromolecular Complex Modeler.
* **Phase 48**: Multi-Omics Pathway Perturbation & Causal Signaling Simulator.
* **Phase 54**: Virtual High-Throughput Screening (vHTS) & Billion-Molecule Docking Grid.
* **Phase 69**: Biotherapeutic Protein Stability & Spatial Aggregation Propensity (SAP) Forecaster.
* **Phase 71**: In-Silico Toxicity & QSAR Mutagenicity Profiler (Ames, hERG, DILI, CYP450).
* **Phase 78**: Chemogenomics Polypharmacology & Off-Target Interactome Engine (Gini Index).
* **Phase 79**: Single-Molecule FRET (smFRET) Kinetics & Hidden Markov Model Transition Engine.
* **Phase 81**: Synthetic Cell Membrane Dynamics & Lipid Nanoparticle (LNP) Formulation Simulator.

### 4. Translational Medicine, Clinical Trials & Pharmacovigilance
* **Phase 34**: Patent Landscape Analysis, 35 U.S.C. 102/103 Prior Art Claim Charts, and FTO Clearance.
* **Phase 36**: Clinical Trial Protocol Designer, PICO Eligibility Criteria, and eCTD Regulatory Package.
* **Phase 46**: Clinical Trial Protocol Optimizer & Patient-Cohort Stratifier.
* **Phase 49**: Real-World Evidence (RWE) & Pharmacovigilance Disproportionality Signal Detector.
* **Phase 66**: Cell Therapy CAR-T Engineering & ASTCT Cytokine Release Syndrome (CRS) Forecaster.
* **Phase 73**: Clinical Trial Site Selection & Protocol Accrual Feasibility Forecaster.
* **Phase 75**: Liquid Biopsy ctDNA Fragmentomics & Longitudinal Minimal Residual Disease (MRD) Engine.
* **Phase 76**: Real-World Safety Signal Mining Sentinel (PRR, ROR, IC025, EBGM).
* **Phase 80**: Multi-Modal Biomarker Discovery & Multi-Omics Signature Extractor (ElasticNet/AUROC).

### 5. Laboratory Automation, Imaging & Biophysics
* **Phase 37**: Robotic Wet-Lab Automation Protocol Compiler (Opentrons v2, PyLabRobot, Autoprotocol).
* **Phase 53**: Multi-Modal Electronic Lab Notebook (ELN) with 21 CFR Part 11 Cryptographic Audit Trails.
* **Phase 68**: High-Throughput Screening (HTS) Assay Robotics & Flow Cytometry Gating Tree Engine.
* **Phase 77**: Cryo-Electron Tomography (Cryo-ET) Subtomogram Averaging & Missing-Wedge Filter.

### 6. Enterprise Infrastructure, Platform & Developer Ecosystem
* **Phases 16–17**: Persistent Cross-Session Research Memory and Relational GraphRAG Knowledge Graph.
* **Phases 18–19**: Multi-Tenant Workspaces, RBAC Roles, Team Collaboration, and Report Annotations.
* **Phases 20–22**: Intelligent Model Pareto Routing, Benchmark Evaluation, and Agent Telemetry.
* **Phases 23–25**: KMS Envelope Encryption, Merkle Audit Trails, Distributed Task Worker Cluster, S3 Vault, and Scoped Developer REST Gateway.
* **Phase 26**: Autonomous Scheduled Research Sweeps, Semantic Diff Engine, and Multi-Channel Alerts.
* **Phase 32**: Real-Time Collaborative 2D Spatial Research Canvas.
* **Phase 52**: Scientific Multi-Modal Data Lakehouse with Parquet/Iceberg Storage and Vector Indices.
* **Official SDKs**: Full-featured Async Python SDK (`packages/sdk-python`) and Isomorphic TypeScript SDK (`apps/web/src/sdk/client.ts`).

---

## 📊 Platform Evolution Status

```
Phase 1: Foundation                  [████████████████████] 100%
Phase 2: Research MVP                [████████████████████] 100%
Phase 3: Multimodal Ingestion        [████████████████████] 100%
Phase 4: Agentic System              [████████████████████] 100%
Phase 5: RAG / Knowledge Core        [████████████████████] 100%
Phase 6: Production / Security       [████████████████████] 100%
Phase 7: Application Maturity        [████████████████████] 100%
Phase 8A: Intelligent Model Routing  [████████████████████] 100%
Phase 8B: Usage Tracking & Quotas    [████████████████████] 100%
Phase 9: Intelligent Knowledge Auto  [████████████████████] 100%
Phase 10: Evidence & Citation Intel  [████████████████████] 100%
Phase 11: Advanced Research Planning [████████████████████] 100%
Phase 12: Advanced Multimodal Intel  [████████████████████] 100%
Phase 13: Dataset & Data Analysis    [████████████████████] 100%
Phase 14: Document & Paper Intel     [████████████████████] 100%
Phase 15: Deep Research Engine       [████████████████████] 100%
Phase 16: Research Memory            [████████████████████] 100%
Phase 17: Long-Term Knowledge Graph  [████████████████████] 100%
Phase 18: Projects & Workspaces      [████████████████████] 100%
Phase 19: Team Collaboration         [████████████████████] 100%
Phase 20: Intelligent Model Ecosys   [████████████████████] 100%
Phase 21: Model Evaluation System    [████████████████████] 100%
Phase 22: Agent Evaluation           [████████████████████] 100%
Phase 23: Enterprise Security        [████████████████████] 100%
Phase 24: Production Infrastructure  [████████████████████] 100%
Phase 25: Public API & Dev Platform  [████████████████████] 100%
Phase 26: Research Automation        [████████████████████] 100%
Phase 27: Multi-Agent Debate Engine  [████████████████████] 100%
Phase 28: Systematic Literature Rev  [████████████████████] 100%
Phase 29: In-Silico Reproducibility  [████████████████████] 100%
Phase 30: Multimodal Presentation    [████████████████████] 100%
Phase 31: Peer Review & Publishing   [████████████████████] 100%
Phase 32: Research Canvas Studio     [████████████████████] 100%
Phase 33: Synthetic Dataset Gen      [████████████████████] 100%
Phase 34: Patent Landscape & FTO     [████████████████████] 100%
Phase 35: Scientific Grant Studio    [████████████████████] 100%
Phase 36: Clinical Trials & Repurp   [████████████████████] 100%
Phase 37: Robotic Lab Automation     [████████████████████] 100%
Phase 38: Bio-Molecular 3D Structure [████████████████████] 100%
Phase 39: MD Trajectory & Quantum    [████████████████████] 100%
Phase 40: CRISPR & Synthetic Biology [████████████████████] 100%
Phase 41: Single-Cell Transcriptomics[████████████████████] 100%
Phase 42: Spatial Microenvironment   [████████████████████] 100%
Phase 43: Generative Chemistry VAE   [████████████████████] 100%
Phase 44: Knowledge Super-Graph      [████████████████████] 100%
Phase 45: Drug Synergy Simulator     [████████████████████] 100%
Phase 46: Clinical Trial Optimizer   [████████████████████] 100%
Phase 47: Cryo-EM Density Modeler    [████████████████████] 100%
Phase 48: Multi-Omics Perturbation   [████████████████████] 100%
Phase 49: Pharmacovigilance Signals  [████████████████████] 100%
Phase 50: AI Scientist Self-Evolving [████████████████████] 100%
Phase 51: RAGAS & Red-Teaming Gate   [████████████████████] 100%
Phase 52: Multi-Modal Data Lakehouse [████████████████████] 100%
Phase 53: Electronic Lab Notebook ELN[████████████████████] 100%
Phase 54: Virtual Screening vHTS     [████████████████████] 100%
Phase 55: Computational Immunology   [████████████████████] 100%
Phase 56: Epigenomics ATAC-seq Peak  [████████████████████] 100%
Phase 57: Protein-Protein PPI Network[████████████████████] 100%
Phase 58: Spatial Metabolomics IMS   [████████████████████] 100%
Phase 59: Antibody-Drug Conjugate ADC[████████████████████] 100%
Phase 60: PBPK Nanomedicine Transport[████████████████████] 100%
Phase 61: Rare Disease Phenotype HPO [████████████████████] 100%
Phase 62: Bioprocess Digital Twin    [████████████████████] 100%
Phase 63: Clinical Supply Chain GxP  [████████████████████] 100%
Phase 64: Referee Panel & Rebuttals  [████████████████████] 100%
Phase 65: Synthetic DNA Logic Gates  [████████████████████] 100%
Phase 66: Cell Therapy CAR-T Studio  [████████████████████] 100%
Phase 67: Neoepitope Cancer Vaccines [████████████████████] 100%
Phase 68: HTS Flow Cytometry Gating  [████████████████████] 100%
Phase 69: Biotherapeutic Stability   [████████████████████] 100%
Phase 70: CRISPR Synthetic Lethality [████████████████████] 100%
Phase 71: In-Silico Toxicity QSAR    [████████████████████] 100%
Phase 72: Gene Circuit Burden IFFL   [████████████████████] 100%
Phase 73: Clinical Site Feasibility  [████████████████████] 100%
Phase 74: Genomic Variant ACMG Class [████████████████████] 100%
Phase 75: Liquid Biopsy ctDNA MRD    [████████████████████] 100%
Phase 76: Real-World Safety Sentinel [████████████████████] 100%
Phase 77: Cryo-ET Subtomogram Average[████████████████████] 100%
Phase 78: Chemogenomics Polypharm    [████████████████████] 100%
Phase 79: smFRET Conformational HMM  [████████████████████] 100%
Phase 80: Multi-Omics Biomarkers     [████████████████████] 100%
Phase 81: Membrane LNP Simulator     [████████████████████] 100%
Phase 82: Metagenomic AMR Resistome  [████████████████████] 100%
─────────────────────────────────────────────────────────────────────────────────
ALL 82 PHASES (GENERATIONS 1 - 52) COMPLETED & FULLY ACTIVE (540+ TESTS PASSING)
```

---

## 🛠️ Monorepo Architecture

```
.
├── apps/
│   ├── api/                     # FastAPI backend application (82 REST routers + WebSockets)
│   │   ├── src/api/             # Routers, dependencies, auth & middlewares
│   │   └── tests/               # API route integration test suites
│   └── web/                     # React 18 + TypeScript + Vite frontend
│       ├── src/components/      # Navigation, Layout, Canvas, Modals
│       ├── src/pages/           # 82 Dedicated Research Studios & Observability pages
│       ├── src/services/        # API & WebSocket client adapters
│       └── src/sdk/             # Official Isomorphic TypeScript Client SDK
│
├── packages/                    # Modular Python shared libraries
│   ├── ai/                      # ModelRegistry, ProviderRegistry, Pareto Router, Gateway
│   ├── agents/                  # Planner, Web, Doc, Critic, Report, Debate Agents
│   ├── research/                # Pipeline orchestrator, DAG runner, 82 computational engines
│   ├── ingestion/               # Parsers (PDF, DOCX, Images, Audio, Video, PDB, FASTQ)
│   ├── retrieval/               # ChromaStore, InMemoryStore, BM25, Hybrid RRF Retriever
│   ├── database/                # SQLAlchemy async models (82 schemas), repositories, Alembic
│   ├── tools/                   # Tool registry, SSRF-safe WebFetch, Code Sandbox, Math
│   ├── shared/                  # Config, structlog, JWT auth, security filters, exceptions
│   └── sdk-python/              # Official Async Python Developer SDK
│
├── docs/                        # Formal ADRs (ADR 001 - ADR 082), PRD, TRD, architecture
├── infrastructure/              # Docker Compose, Kubernetes manifests, Prometheus configs
└── pyproject.toml               # Monorepo workspace configuration
```

---

## 💻 Quick Start

### 1. Environment Configuration
```bash
cp .env.example .env
# Set GEMINI_API_KEY, OPENAI_API_KEY, or point to local Ollama instance
```

### 2. Launch Local Database & Services
```bash
docker compose up -d
```
Spins up PostgreSQL 16 (`5432`), ChromaDB (`8000`), Redis (`6379`), and Ollama (`11434`).

### 3. Start Backend Services
```bash
cd apps/api
pip install -e ".[dev]"

# Run database migrations
alembic upgrade head

# Start FastAPI ASGI server
uvicorn src.main:app --reload --port 8000
```
* **Interactive OpenAPI Specs**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **System Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### 4. Start Web Application
```bash
cd apps/web
npm install
npm run dev
```
* **Web Application UI**: [http://localhost:5173](http://localhost:5173)

---

## 🧪 Testing & Verification

The repository enforces strict continuous integration across **Python 3.11, 3.12, 3.13**, frontend TypeScript compilation, and Docker builds.

```bash
# Run all unit and integration test suites
pytest packages/ apps/api/tests/ -v

# Run domain-specific tests
pytest packages/research/tests/ -v
pytest packages/database/tests/ -v
pytest apps/api/tests/ -v

# Run with test coverage
pytest --cov=packages --cov=apps/api

# Build and validate frontend TypeScript bundle
cd apps/web
npm run build
npm run lint
```

---

## 📦 Developer SDK Usage

### Python SDK (`packages/sdk-python`)
```python
import asyncio
from ai_research_os import ResearchClient

async def main():
    async with ResearchClient(base_url="http://localhost:8000", api_key="sk_live_demo") as client:
        # Launch an in-silico CAR-T cytotoxicity simulation
        cart_sim = await client.cart.simulate(
            target_antigen="CD19",
            scfv_clone="FMC63",
            costimulatory_domain="4-1BB"
        )
        print("Predicted Tumor Lysis:", cart_sim.cytotoxicity_lysis_pct)

asyncio.run(main())
```

### TypeScript SDK (`apps/web/src/sdk`)
```typescript
import { ResearchClient } from './sdk/client';

const client = new ResearchClient({ baseUrl: 'http://localhost:8000', apiKey: 'sk_live_demo' });

async function runAnalysis() {
  const result = await client.variants.classifyACMG({
    gene_symbol: 'BRCA1',
    hgvs_c: 'c.5266dupC',
    alphamissense_score: 0.95
  });
  console.log('ACMG Class:', result.acmg_class);
}
```

---

## 🔒 Security, Compliance & Safety Guarantees

1. **Air-Gapped & Local-First Execution**: The platform operates 100% locally with Ollama and self-hosted vector stores without sending sensitive biomedical data externally.
2. **SSRF Defensive Filtering**: `WebFetchTool` inspects all resolved DNS addresses and blocks private (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), loopback (`127.0.0.1`), metadata endpoints (`169.254.169.254`), and cloud link-local IPs.
3. **21 CFR Part 11 & GxP Compliance**: Electronic signatures, cryptographic SHA-256 audit chaining, and timestamped witness approvals.
4. **Deterministic Calculation Engines**: Mathematical, kinetic, statistical, and genomic formulas execute in sandboxed Python engines rather than probabilistic LLM approximations.

---

## 📜 License & Citation

Distributed under the **Apache 2.0 License**.

If you use the **Agentic Multimodal Research Platform (AI Research OS)** in your research or production systems, please cite:

```bibtex
@software{talaviya2026researchos,
  author = {Om Talaviya},
  title = {Agentic Multimodal Research Platform: An Autonomous Multi-Disciplinary AI Research Operating System},
  year = {2026},
  url = {https://github.com/Om-Talaviya/agentic-multimodal-research-platform},
  version = {1.1}
}
```