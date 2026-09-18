# Changelog: CHANGELOG.md

All notable changes to the **Agentic Multimodal Research Platform** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.3.0] - 2026-09-18 (Branch: `develop/v1.1`)

### Added
- **Phase 90: Multi-Omics Epigenetic Age & DNA Methylation Clock Predictor**:
  - Implemented `EpigeneticClockEngine` supporting Horvath (353-CpG), Hannum (71-CpG), PhenoAge, and GrimAge models with missing site imputation, Epigenetic Age Acceleration (EAA), and DunedinPACE pace of aging.
  - Created `DBEpigeneticSample`, `DBMethylationClockResult`, `DBCpGMarkerScore` models and `EpigeneticClockRepository`.
  - Added REST API endpoints under `/api/v1/epigenetic-clock/*`.
- **Phase 91: High-Content Phenotypic Image Screening & Single-Cell Morphometry AI**:
  - Implemented `PhenotypicScreeningEngine` analyzing 5-channel Cell Painting assays (DNA, RNA, ER, AGP, Mito) with Haralick texture, Zernike moments, Mahalanobis phenotypic distance, and Mechanism-of-Action (MoA) classification.
  - Created `DBCellPaintingPlate`, `DBCellPaintingWell`, `DBSingleCellMorphometry` models and `PhenotypicScreeningRepository`.
  - Added REST API endpoints under `/api/v1/phenotypic-screening/*`.
- **Phase 92: Synthetic Biology Gene Circuit Design & Boolean Logic Gate Synthesizer**:
  - Implemented `SyntheticGeneCircuitEngine` with transcriptional logic gates (AND, OR, NAND, NOR, XOR), transcription factor assignment (TetR, LacI, AraC, LuxR), Hill kinetic dynamic ODE simulation, and Golden Gate MoClo plasmid overhang compilation.
  - Created `DBSyntheticGeneCircuit`, `DBBioLogicGate`, `DBCircuitKineticsTrace` models and `SyntheticGeneCircuitRepository`.
  - Added REST API endpoints under `/api/v1/synthetic-gene-circuits/*`.
- **Phase 93: Autonomous Preclinical Toxicogenomics & ADMET-Safety Risk Ranker**:
  - Implemented `PreclinicalToxicologyEngine` with Ames mutagenicity, hERG cardiotoxicity ($IC_{50}$), DILI hepatotoxicity, CYP450 inhibition profiles, Caco-2 permeability, structural alert scanning, and composite Therapeutic Safety Index (TSI) scoring.
  - Created `DBPreclinicalToxStudy`, `DBToxicogenomicEndpoint`, `DBStructuralToxAlert` models and `PreclinicalToxicologyRepository`.
  - Added REST API endpoints under `/api/v1/preclinical-toxicology/*`.

---

## [1.2.0] - 2026-09-18 (Branch: `develop/v1.1`)

### Added
- **Phase 83: Autonomous Quantum Chemistry & Molecular Hamiltonian VQE Simulation Engine**:
  - Implemented `QuantumChemistryVQEEngine` with Jordan-Wigner transformation, UCCSD ansatz parametrization, and classical gradient optimization achieving chemical accuracy ($\Delta E \le 1.0\text{ kcal/mol}$).
  - Created `DBQuantumMolecularSystem`, `DBVQEAnsatzExecution`, `DBHamiltonianEnergyState` models and `QuantumChemistryRepository`.
  - Added REST API routes under `/api/v1/quantum-chemistry/*`.
- **Phase 84: Autonomous Next-Generation Sequencing (NGS) Long-Read Structural Variant & Telomere Calling Engine**:
  - Implemented `LongReadGenomicsEngine` for PacBio HiFi and Oxford Nanopore CIGAR alignment parsing, structural variant calling (DEL, INS, DUP, INV, TRA), and hexamer `TTAGGG` repeat erosion profiling.
  - Created `DBLongReadSequencingRun`, `DBStructuralVariantCall`, `DBTelomericRepeatProfile` models and `LongReadGenomicsRepository`.
  - Added REST API routes under `/api/v1/long-read/*`.
- **Phase 85: Autonomous Multi-Modal Diffusion-Based 3D Protein-Ligand Complex Conformation Generator**:
  - Implemented `DiffusionConformationEngine` utilizing SE(3)-equivariant score matching reverse diffusion to sample docking conformations and binding pocket druggability.
  - Created `DBDiffusionComplexJob`, `DBDiffusionPocketConformation`, `DBEquivariantDockingPose` models and `DiffusionConformationRepository`.
  - Added REST API routes under `/api/v1/diffusion-conformation/*`.
- **Phase 86: Autonomous Whole-Cell Metabolic Flux Simulation & Kinetic Genome-Scale Dynamic Modeler**:
  - Implemented `WholeCellMetabolicEngine` for dynamic Flux Balance Analysis (dFBA), biomass optimization, and glucose-acetate kinetic traces.
  - Created `DBWholeCellModel`, `DBMetabolicFluxState`, `DBKineticSimulationTrace` models and `WholeCellMetabolicRepository`.
  - Added REST API routes under `/api/v1/whole-cell/*`.
- **Phase 87: Autonomous Clinical Genomics Digital Twin & Patient-Specific Pharmacogenomics Engine**:
  - Implemented `ClinicalGenomicsTwinEngine` matching CPIC Level A diplotypes and calculating patient-specific clearance curves, toxic plasma accumulation risk, and dose adjustments.
  - Created `DBPatientGenomicProfile`, `DBPharmacogenomicGuideline`, `DBPatientDigitalTwinSim` models and `ClinicalGenomicsTwinRepository`.
  - Added REST API routes under `/api/v1/clinical-twin/*`.
- **Phase 88: Autonomous Radiogenomics & 3D Volumetric Medical Imaging AI Feature Extractor**:
  - Implemented `RadiogenomicsEngine` for IBSI 3D shape, intensity histogram, and GLCM texture extraction correlated with oncogenomic alterations (IDH1, EGFR, MGMT).
  - Created `DBRadiogenomicsScan`, `DBVolumetricRadiomicFeature`, `DBImagingGenomicCorrelation` models and `RadiogenomicsRepository`.
  - Added REST API routes under `/api/v1/radiogenomics/*`.
- **Phase 89: Autonomous Laboratory Robotics Automation & Self-Driving Workcell Protocol Compiler**:
  - Implemented `RoboticWorkcellEngine` compiling executable Python protocol scripts (Opentrons API v2 / PyLabRobot) with liquid class modeling and deck collision checking.
  - Created `DBRoboticWorkcellProtocol`, `DBDeckLayoutInstruction`, `DBAutomatedRunExecution` models and `RoboticWorkcellRepository`.
  - Added REST API routes under `/api/v1/robotic-workcell/*`.

---

## [1.1.0] - 2026-09-12 (Branch: `develop/v1.1`)

### Added
- **Phase 15: Deep Research Engine**:
  - Implemented `DeepResearchEngine` in `packages/research/src/research/deep_research.py` orchestrating autonomous multi-round recursive research loops, iterative hypothesis formulation, and dynamic DAG subtask rescheduling.
  - Added `DeepResearchConfig` and `ResearchIteration` data structures in `packages/research/src/research/models.py` tracking iteration index, hypothesis formulation, targeted subtasks, and quantitative confidence progression.
  - Upgraded `CriticAgent` in `packages/agents/src/agents/critic/critic_agent.py` to audit evidence coverage, isolate unresolved gaps (`gap_queries`), and formulate testable `suggested_hypotheses`.
  - Enhanced `PlannerAgent.replan()` in `packages/agents/src/agents/planner/planner_agent.py` to accept deep iteration indices and transform gap queries and hypotheses into prioritized investigation subtasks.
  - Enforced 3 strict convergence guardrails: target confidence threshold ($\tau \ge 0.85$), maximum iteration ceiling (`max_iterations`, default: 3, max: 5), and diminishing returns cutoff ($\Delta \tau < 0.02$ across rounds).
  - Defined real-time deep research event types (`DEEP_RESEARCH_STARTED`, `RESEARCH_ITERATION_STARTED`, `HYPOTHESIS_FORMULATED`, `RESEARCH_ITERATION_COMPLETED`, `DEEP_RESEARCH_CONVERGED`, `DEEP_RESEARCH_TERMINATED`) with live WebSocket broadcasting.
  - Built `DeepResearchTracker.tsx` in `apps/web/src/components/` with multi-round iteration stepper, confidence convergence gauge, hypothesis status badges, and gap resolution explorer.
  - Added unit test suites in `packages/research/tests/test_deep_research.py` and `packages/agents/tests/test_deep_critic.py`, achieving 100% pass rate across all 247 tests.
- **Phase 14: Document & Paper Intelligence**:
  - Implemented `AcademicPaperParser` in `packages/ingestion/src/ingestion/parsers/academic.py` extracting hierarchical section trees (`PaperSection`), metadata (title, authors, affiliations, abstract), LaTeX/markdown formulas, and explicit limitations.
  - Implemented `BibEntry` bibliographic extraction and citation anchoring, mapping inline references (`[1]`, `(Author et al., 2024)`) directly to bibliography entries with DOI and arXiv metadata.
  - Enhanced `SemanticChunker` with academic section-aware boundary chunking, preserving section titles and types (`methodology`, `results`, `limitations`) for fine-grained hybrid RAG retrieval.
  - Created `PaperAnalysisTool` and `MethodologyComparisonTool` in `packages/tools/src/tools/definitions/paper_analysis.py` for automated extraction of research dimensions and multi-paper comparative matrices.
  - Equipped `DocumentAnalysisAgent` with academic paper parsing and comparative analysis tools.
  - Created `PaperViewer.tsx` (interactive section navigation tree, citation popovers, limitations card) and `ComparisonMatrix.tsx` (cross-paper methodology diffs) in `apps/web`.
  - Added unit test suites in `packages/ingestion/tests/test_academic_parser.py` and `packages/tools/tests/test_paper_analysis.py`.
- **Phase 13: Dataset & Data Analysis Intelligence**:
  - Implemented `TabularParser` in `packages/ingestion/src/ingestion/parsers/tabular.py` supporting `.csv`, `.tsv`, `.xlsx`, `.xls`, and `.json` datasets with automated delimiter sniffing, schema type inference, column distribution profiling (mean, median, std dev, min/max, nulls, unique count), and Markdown summary table formatting.
  - Implemented `DataAnalysisTool` in `packages/tools/src/tools/definitions/data_analysis.py` providing deterministic calculations for descriptive statistics, multi-column group-by aggregations (`sum`, `mean`, `median`, `min`, `max`, `count`), Pearson correlation coefficients, linear regression modeling (slope, intercept, $R^2$), and relational record filtering.
  - Implemented `DeterministicMathTool` enforcing **ADR 007** and **ADR 013** zero-hallucination standards via safe recursive Python Abstract Syntax Tree (AST) expression evaluation.
  - Equipped `DocumentAnalysisAgent` with `DataAnalysisTool` and `DeterministicMathTool` for autonomous investigation of structured data files.
  - Enhanced `SemanticChunker` with dataset profile chunking, making column metadata, statistics, and sample rows searchable via dense vector and BM25 RRF hybrid retrieval.
  - Whitelisted dataset formats (`CSV`, `TSV`, `EXCEL`, `JSON`) in `DocumentFormat`, `SourceType`, and the FastAPI document upload route.
  - Developed `DatasetViewer.tsx` React component with interactive tabbed views for dataset summaries, column metrics, and raw sample records.
  - Added unit test suites in `packages/ingestion/tests/test_tabular_parser.py` and `packages/tools/tests/test_data_analysis_tool.py`.
- **Phase 12: Advanced Multimodal Research**:
  - Extended `CitationCoordinates` with `timestamp_start`, `timestamp_end`, `media_type`, `speaker`, and `chart_data` across models and schemas.
  - Implemented `AudioParser` for speech audio formats (`.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`, `.aac`) extracting timestamped dialogue segments (`[MM:SS - MM:SS]`) and speaker attribution.
  - Implemented `VideoParser` for video media (`.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`) creating synchronized chronological timeline transcripts, visual events, and keyframe metadata.
  - Upgraded `ImageParser` to detect scientific figures and plots, producing structured `ChartRef` models with JSON data series and Markdown data tables.
  - Enhanced `SemanticChunker` with multimodal segmentation, generating timestamp-bounded audio/video chunks and structured chart chunks for vector and BM25 RRF indexing.
  - Whitelisted audio and video MIME types and file extensions in FastAPI document upload endpoints.
  - Created `MultimodalEvidenceViewer.tsx` studio component in React frontend for interactive inspection of media citations, timestamp ranges, speakers, and chart data series.
  - Added unit test suite in `packages/ingestion/tests/test_multimodal_audio_video.py`.
- **Phase 11: Advanced Research Planning**:
  - Implemented hierarchical Subquestion Decomposition and Query Trees (`QueryTreeNode`) for multi-level strategic planning.
  - Added quantitative ambiguity evaluation (`ambiguity_score`) and autonomous parameterization of research boundaries (`InferredScope`).
  - Added dynamic agent role and capability matching, mapping sub-inquiries to specialized agent personas with execution contracts.
  - Implemented closed-loop Adaptive Replanning (`PlannerAgent.replan()`) triggered dynamically when `CriticAgent` detects evidentiary gaps or critical contradictions during execution.
  - Extended `ResearchTask` and `DBResearchTask` with `parent_task_id`, `is_dynamic`, and `depth` metadata.
  - Added `plan_decomposed`, `task_spawned`, and `dag_replanned` WebSocket events to `ResearchEventType`.
  - Created interactive `QueryTreeViewer.tsx` React component in `apps/web` with branch expand/collapse, ambiguity indicators, and live execution status.
  - Added unit test suite in `packages/agents/tests/test_planner_advanced_planning.py`.
- **Phase 10: Evidence & Citation Intelligence**:
  - Implemented fine-grained claim extraction and coordinate anchoring (`CitationCoordinates`) mapping claims to exact document coordinates (`page_number`, `paragraph_index`, `table_row`, `table_col`, `char_start`, `char_end`, `exact_quote`).
  - Added structured `Citation` and `Contradiction` models with SQLite and PostgreSQL 16 JSONB cross-compatibility.
  - Implemented pairwise Contradiction Detection Engine in `CriticAgent` with classification taxonomy (`direct_conflict`, `numerical_discrepancy`, `methodological_divergence`).
  - Upgraded `ReportAgent` to synthesize nested citations per finding, preserve the contradictions matrix, and calculate an overall quantitative factual confidence score (`confidence_score`).
  - Integrated full end-to-end evidence citation flow across `ResearchPipeline`, database models, and API serialization.
  - Added TypeScript interfaces in `apps/web/src/types/research.ts` (`Citation`, `CitationCoordinates`, `Contradiction`).
  - Added comprehensive test suites: `test_citation_intelligence.py`, `test_critic_contradiction_detection.py`, and `test_report_citation_synthesis.py`.
- **Phase 9: Intelligent Knowledge Automation**:
  - Automated zero-touch ingestion and dual-indexing (`Upload $\rightarrow$ Validate $\rightarrow$ Extract $\rightarrow$ Chunk $\rightarrow$ Embed $\rightarrow$ Index $\rightarrow$ Ready`).
  - Added document processing status lifecycle (`pending` $\rightarrow$ `processing` $\rightarrow$ `ready` / `failed`) in `Document` model and repository.
  - Integrated `KnowledgeIndexer` into `IngestionPipeline` for immediate `VectorStore` (embeddings) and `BM25Index` (lexical tokens) population.
  - Enhanced `PlannerAgent` with knowledge-base awareness, enabling the planner to inspect available domain documents before decomposing inquiries into the Task DAG.
  - Enhanced `DocumentAnalysisAgent` to support hybrid semantic retrieval (`KnowledgeSearchTool`) alongside direct document reading.
  - Added REST endpoints for knowledge base operations: `GET /api/v1/documents/search`, `POST /api/v1/documents/{id}/reindex`, and cascading `DELETE /api/v1/documents/{id}`.
- **Phase 8B: Persistent Usage & Quota Subsystem** (`commit: a603114`):
  - Added `UserQuota` model supporting configurable token and cost limits (`NULL` = unlimited).
  - Added `UsageRecord` model capturing per-inference telemetry (`input_tokens`, `output_tokens`, `total_tokens`, `estimated_cost`, `latency_ms`).
  - Added `UsageRepository` with transactional row-level locking (`SELECT ... FOR UPDATE`) to prevent race conditions during concurrent agent calls.
  - Verified concurrency guarantees with test suite (10 concurrent workers @ 20 tokens against 50-token quota resulting in 0 oversubscription).
  - Added quota-aware model fallback routing.
  - Propagated authenticated `user_id` from JWT auth down into `ResearchPipeline`, `AgentOrchestrator`, and `AgentContext`.
- **Comprehensive Documentation Architecture** (`commit: a00949e`):
  - Established synchronized documentation across `/README.md`, `/AGENTS.md`, `/docs/` (PRD, TRD, ARCHITECTURE, backend-schema, flow, decisions, CHANGELOG), `/design/ui-ux.md`, and `/TODO.md`.
  - Formalized 6-generation product roadmap spanning Phases 9 to 26.
- **Phase 8A: Intelligent Model Routing & Multi-Provider Gateway** (`commit: 88ac57d`):
  - Created `ModelRegistry` dynamic capability catalog (`STREAMING_RESPONSE`, `VISION_ANALYSIS`, `FACTUAL_EXTRACTION`, `SYNTHESIS`).
  - Created `ProviderRegistry` for active provider lifecycle and health monitoring.
  - Created `ModelRouter` for multi-criteria task matching and priority scoring.
  - Created `ModelGateway` for unified completion, streaming, vision invocation, and automated rate limit/error fallback failover.

---

## [1.0.0] - 2026-09-08

### Added
- **Phase 7: Application Maturity & Authentication Completion**:
  - Phase 7.1: Fixed research job response mapping in web dashboard.
  - Phase 7.2: Added persistent PostgreSQL `users` table, Alembic migration (`001_create_users_table.py`), and PBKDF2 password hashing.
  - Phase 7.3: Migrated to official Google Gemini SDK (`ai.providers.gemini.GeminiProvider`); deleted legacy unofficial `GeminiWeb2API`.
  - Added authenticated real-time WebSocket streaming (`/api/v1/research/{id}/ws`) with initial state snapshot hydration.
- **Phase 6: Production & Security**:
  - Added JWT access/refresh token lifecycle and RBAC (`Admin`, `Researcher`, `Viewer`).
  - Added SSRF protection in `WebFetchTool` with strict private IP and metadata endpoint filtering.
  - Added Prometheus metrics exposition (`/metrics`) and Kubernetes deployment manifests.
- **Phase 5: Hybrid RAG & Knowledge Layer**:
  - Implemented Reciprocal Rank Fusion (RRF) combining dense ChromaDB vector search and sparse BM25 lexical search.
  - Added document chunking with metadata preservation.
- **Phase 4: Agentic System Core**:
  - Built autonomous agent hierarchy: `PlannerAgent`, `WebResearchAgent`, `DocumentAnalysisAgent`, `CriticAgent`, and `ReportAgent`.
  - Added DAG execution engine with topological dependency resolution.
- **Phase 3: Multimodal Ingestion Pipeline**:
  - Added native PDF extraction with table detection (`pdfplumber`).
  - Added DOCX extraction (`python-docx`).
  - Added Image extraction via Vision LLMs (`Pillow`).
- **Phase 2: Research MVP**:
  - Implemented initial end-to-end research workflow from inquiry formulation to report generation.
- **Phase 1: Foundation**:
  - Established modular monorepo structure with FastAPI backend, SQLAlchemy 2.0 Async, and React 18 / Vite frontend.
