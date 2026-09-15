
## [Phase 46] - Autonomous Clinical Trial Protocol Optimizer & Patient-Cohort Stratifier
### Added
- Database models: `DBClinicalTrialProtocol`, `DBEligibilityCriterion`, `DBCohortPatientMatch`, `DBSyntheticControlArm`.
- Repository `ClinicalTrialRepository` for CRUD and cascade protocol relations.
- Scientific `ClinicalTrialOptimizerEngine` for Schoenfeld sample-size power estimation and Kaplan-Meier survival curves.
- FastAPI routes at `/api/v1/clinical-trials/*`.
- Interactive React studio `ClinicalTrialStudioPage.tsx` with telemetry gauges and survival curve chart.
- Unit and integration tests in `packages/database/tests/test_clinical_trial_repo.py`, `packages/research/tests/test_clinical_trial_engine.py`, and `apps/api/tests/test_clinical_trial_api.py`.
- Architecture Decision Record **ADR 046**.

# Changelog: CHANGELOG.md

All notable changes to the **Agentic Multimodal Research Platform** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.19.0] - 2026-09-15 (Generation 17: Phase 45 - Autonomous Drug Repurposing & Combination Synergy Simulator)

### Added
- **Phase 45: Autonomous Drug Repurposing & Combination Synergy Simulator**:
  - Implemented database models in `packages/database/src/database/models/drug_synergy.py` (`DBDrugRepurposingScreen`, `DBRepurposedCandidate`, `DBDrugCombinationSynergy`).
  - Implemented `DrugSynergyRepository` in `packages/database/src/database/repositories/drug_synergy_repo.py`.
  - Implemented `DrugSynergyEngine` in `packages/research/src/research/drug_synergy_engine.py`.
  - Implemented REST API routes in `apps/api/src/api/routes/drug_synergy.py`.
  - Created interactive Drug Synergy Studio in `apps/web/src/pages/DrugSynergyStudioPage.tsx`.
  - Added unit and integration test suites in `packages/database/tests/test_drug_synergy_repo.py`, `packages/research/tests/test_drug_synergy_engine.py`, and `apps/api/tests/test_drug_synergy_api.py`.
  - Formalized **ADR 045** in `docs/decisions.md`.

---

## [2.18.0] - 2026-09-15 (Generation 17: Phase 44 - Autonomous Multi-Modal Scientific Knowledge Super-Graph & Hypothesis Discovery Engine)

### Added
- **Phase 44: Autonomous Multi-Modal Scientific Knowledge Super-Graph & Hypothesis Discovery Engine**:
  - Implemented database models in `packages/database/src/database/models/super_graph.py` (`DBSuperGraphNode`, `DBSuperGraphEdge`, `DBCausalHypothesis`).
  - Implemented `SuperGraphRepository` in `packages/database/src/database/repositories/super_graph_repo.py`.
  - Implemented `SuperGraphHypothesisEngine` in `packages/research/src/research/super_graph_engine.py`.
  - Implemented REST API routes in `apps/api/src/api/routes/super_graph.py`.
  - Created interactive Super-Graph Studio in `apps/web/src/pages/SuperGraphStudioPage.tsx`.
  - Added unit and integration test suites in `packages/database/tests/test_super_graph_repo.py`, `packages/research/tests/test_super_graph_engine.py`, and `apps/api/tests/test_super_graph_api.py`.
  - Formalized **ADR 044** in `docs/decisions.md`.

---

## [2.17.0] - 2026-09-15 (Generation 16: Phase 43 - Autonomous De Novo Generative Molecule & Antibody Design Studio)

### Added
- **Phase 43: Autonomous De Novo Generative Molecule & Antibody Design Studio**:
  - Implemented database models in `packages/database/src/database/models/generative_chemistry.py` (`DBGenerativeMolecule`, `DBADMETProfile`, `DBAntibodyCandidate`).
  - Implemented `GenerativeChemistryRepository` in `packages/database/src/database/repositories/generative_chemistry_repo.py`.
  - Implemented `GenerativeChemistryEngine` in `packages/research/src/research/generative_chemistry_engine.py`.
  - Implemented REST API routes in `apps/api/src/api/routes/generative_chemistry.py`.
  - Created interactive Generative Chemistry Studio in `apps/web/src/pages/GenerativeChemistryPage.tsx`.
  - Added unit and integration test suites in `packages/database/tests/test_generative_chemistry_repo.py`, `packages/research/tests/test_generative_chemistry_engine.py`, and `apps/api/tests/test_generative_chemistry_api.py`.
  - Formalized **ADR 043** in `docs/decisions.md`.

---

## [2.16.0] - 2026-09-15 (Generation 16: Phase 42 - Autonomous Spatial Transcriptomics & Tissue Microenvironment Studio)

### Added
- **Phase 42: Autonomous Spatial Transcriptomics & Tissue Microenvironment Studio**:
  - Implemented database models in `packages/database/src/database/models/spatial_transcriptomics.py` (`DBSpatialTissueDataset`, `DBCellSpatialCoordinate`, `DBCellCommunicationPair`, `DBSpatialDomain`).
  - Implemented `SpatialTranscriptomicsRepository` in `packages/database/src/database/repositories/spatial_repo.py` supporting dataset CRUD, coordinate querying, and ligand-receptor crosstalk extraction.
  - Implemented `SpatialTranscriptomicsEngine` in `packages/research/src/research/spatial_engine.py` simulating 2D histological coordinate grids, spatial domain partitioning, and CellChat/CellPhoneDB signaling pathways.
  - Implemented REST API routes in `apps/api/src/api/routes/spatial.py`.
  - Created interactive Spatial Transcriptomics Studio in `apps/web/src/pages/SpatialTranscriptomicsPage.tsx`.
  - Added unit and integration test suites in `packages/database/tests/test_spatial_repo.py`, `packages/research/tests/test_spatial_engine.py`, and `apps/api/tests/test_spatial_api.py`.
  - Formalized **ADR 042** in `docs/decisions.md`.

---

## [2.15.0] - 2026-09-15 (Generation 15: Phase 41 - Autonomous Multi-Omics & Single-Cell Transcriptomics Differential Expression Studio)

### Added
- **Phase 41: Autonomous Multi-Omics & Single-Cell Transcriptomics Differential Expression Studio**:
  - Implemented database models in `packages/database/src/database/models/single_cell.py` (`DBSingleCellDataset`, `DBCellCluster`, `DBCellCoordinate`, `DBDifferentialGene`, `DBPathwayEnrichment`) with cross-dialect `GUID()`, JSONB variants, cascade relations, and timezone-aware timestamps.
  - Implemented `SingleCellRepository` in `packages/database/src/database/repositories/single_cell_repo.py` supporting single-cell dataset lifecycles, cluster distributions, high-dimensional coordinates, marker gene discoveries, and GSEA pathway enrichments.
  - Implemented `SingleCellTranscriptomicsEngine` in `packages/research/src/research/single_cell_engine.py`:
    - Quality Control (QC) filtering pipeline on UMI library depth, detected gene count, and mitochondrial read percentage ($\le 15\%$).
    - Graph-based Leiden community clustering and Principal Component Analysis (PCA) dimensionality reduction.
    - 2D nonlinear embedding projection generating high-resolution coordinates for both Uniform Manifold Approximation and Projection (UMAP) and $t$-Distributed Stochastic Neighbor Embedding (t-SNE).
    - Non-parametric Wilcoxon rank-sum differential expression testing with Benjamini-Hochberg False Discovery Rate (FDR) adjusted $p$-values and $\log_2\text{FC}$ effect sizes.
    - Diffusion Pseudotime (DPT) cellular trajectory ordering ($0.0 \rightarrow 1.0$) mapping stem/quiescent state transitions toward lineage endpoints.
    - Gene Set Enrichment Analysis (GSEA) over-representation scoring across MSigDB Hallmark, KEGG, and Reactome pathways with Normalized Enrichment Scores (NES).
  - Implemented REST API routes in `apps/api/src/api/routes/single_cell.py`:
    - `POST /api/v1/single-cell/analyze`: Run end-to-end single-cell transcriptomics analysis pipeline.
    - `GET /api/v1/single-cell/datasets`: List scRNA-seq datasets with filtering.
    - `GET /api/v1/single-cell/datasets/{id}`: Detailed dataset inspection with clusters and pathway enrichments.
    - `GET /api/v1/single-cell/datasets/{id}/coordinates`: Fetch 2D UMAP/t-SNE coordinates with optional cluster filtering and downsampling.
    - `GET /api/v1/single-cell/datasets/{id}/markers`: Fetch cluster-specific differential marker genes.
    - `DELETE /api/v1/single-cell/datasets/{id}`: Delete dataset and cascaded records.
  - Created interactive Single-Cell Transcriptomics Studio in `apps/web/src/pages/SingleCellStudioPage.tsx`:
    - 2D UMAP/t-SNE Scatter Plot Canvas with cluster color-coding, cell-type gating, and interactive tooltips.
    - Cell Cluster Composition Distribution cards with top distinguishing markers.
    - Differential Expression Volcano Plot with fold change and FDR significance thresholds.
    - Cluster-Specific Marker Genes Table with export and search.
    - Diffusion Pseudotime Trajectory Bar Graphs showing differentiation progression.
    - Gene Set Enrichment Analysis (GSEA) Pathway Waterfall.
    - Preloaded single-cell study presets (Human Hepatocyte LNP Atlas, PBMC Immune Profiling, Neural Lineage Dynamics).
  - Mounted `/single-cell` route in `App.tsx` and added `Single-Cell Multi-Omics` navigation link with `Microscope` icon in `Layout.tsx`.
  - Added unit and integration test suites in `packages/database/tests/test_single_cell_repo.py`, `packages/research/tests/test_single_cell_engine.py`, and `apps/api/tests/test_single_cell_api.py` (410/410 monorepo tests passing).
  - Updated `scripts/seed_demo_data.py` with Human Primary Hepatocyte LNP-CRISPR scRNA-seq Atlas.
  - Formalized **ADR 041** in `docs/decisions.md`.

---

## [2.14.0] - 2026-09-15 (Generation 14: Phase 40 - Autonomous Synthetic Biology & CRISPR Gene Editing Guide RNA Design Studio)

### Added
- **Phase 40: Autonomous Synthetic Biology & CRISPR Gene Editing Guide RNA Design Studio**:
  - Implemented database models in `packages/database/src/database/models/crispr.py` (`DBCRISPRDesign`, `DBGuideRNA`, `DBOffTargetSite`, `DBBaseEditingProfile`) with cross-dialect `GUID()`, JSONB variants, cascade relations, and timezone-aware timestamps.
  - Implemented `CRISPRRepository` in `packages/database/src/database/repositories/crispr_repo.py` supporting targeting campaign lifecycle, candidate gRNA ranking, genome-wide off-target mismatch loci, and precision base editing profiles.
  - Implemented `CRISPRGuideDesignEngine` in `packages/research/src/research/crispr_engine.py`:
    - PAM scanning across nucleases: SpCas9 (`NGG`), Cas12a/Cpf1 (`TTTV`), xCas9 (`NG`), SaCas9 (`NNGRRT`), and Cas9-HF1.
    - Azimuth 2.0 / Rule Set 2 on-target cleavage efficiency scoring (0–100%) incorporating positional base preferences and GC penalty windows.
    - Cutting Frequency Determination (CFD) off-target positional mismatch matrix scoring against genome-wide loci.
    - Precision Base Editing deamination activity window profiling (positions 4–8 for ABE $A \rightarrow G$ and CBE $C \rightarrow T$) with bystander mutation risk classification.
    - Golden Gate cloning oligonucleotide generation with BsmBI/BsaI sticky overhangs (`5'-CACC-[Spacer]-3'` and `5'-AAAC-[RevComp]-3'`) and duplex annealing thermocycler protocols.
  - Implemented REST API routes in `apps/api/src/api/routes/crispr.py`:
    - `POST /api/v1/crispr/design`: Design candidate gRNAs, off-target analysis, base editing profiles, and cloning oligos.
    - `GET /api/v1/crispr/designs`: List targeting campaigns with filtering.
    - `GET /api/v1/crispr/designs/{id}`: Detailed campaign inspection with full candidate guides, off-targets, and base editing profiles.
    - `GET /api/v1/crispr/guides/{id}/oligos`: Retrieve ready-to-order Golden Gate cloning oligos and annealing protocol.
    - `GET /api/v1/crispr/designs/{id}/export-genbank`: Download annotated GenBank (.gb) format sequence file.
    - `DELETE /api/v1/crispr/designs/{id}`: Delete targeting campaign and cascaded records.
  - Created interactive CRISPR & Synthetic Biology Studio in `apps/web/src/pages/CRISPRStudioPage.tsx`:
    - Protospacer Sequence Map Visualizer with highlighted PAM sites and active guide footprints.
    - Candidate gRNA Ranked Table with Azimuth efficiency, CFD specificity, GC%, and Quality Tier badges.
    - Genome-Wide Off-Target Inspector with mismatch counts and exonic vs intergenic risk tags.
    - Precision Base Editing Window Visualizer for ABE8e and CBE deamination windows.
    - Golden Gate BsmBI/BsaI Cloning Oligo ordering sheet with 1-click clipboard copy and GenBank download.
    - Preloaded therapeutic targeting presets (PCSK9 Exon 1, BCL11A Enhancer, VEGFA Exon 3).
  - Mounted `/crispr` route in `App.tsx` and added `CRISPR & Synthetic Bio` navigation link with `Scissors` icon in `Layout.tsx`.
  - Added unit and integration test suites in `packages/database/tests/test_crispr_repo.py`, `packages/research/tests/test_crispr_engine.py`, and `apps/api/tests/test_crispr_api.py` (407/407 monorepo tests passing).
  - Updated `scripts/seed_demo_data.py` with PCSK9 Exon 1 targeting campaign.
  - Formalized **ADR 040** in `docs/decisions.md`.

---

## [2.13.0] - 2026-09-15 (Generation 13: Phase 39 - Autonomous Molecular Dynamics Trajectory & Quantum Chemistry Simulation Studio)

### Added
- **Phase 39: Autonomous Molecular Dynamics Trajectory & Quantum Chemistry Simulation Studio**:
  - Implemented database models in `packages/database/src/database/models/molecular_dynamics.py` (`DBMolecularDynamicsSimulation`, `DBTrajectoryFrame`, `DBResidueFluctuation`, `DBQuantumChemistryProperty`) with cross-dialect `GUID()`, JSONB variants, cascade relations, and timezone-aware timestamps.
  - Implemented `MolecularDynamicsRepository` in `packages/database/src/database/repositories/molecular_dynamics_repo.py` supporting time-series simulations, multi-frame snapshots, per-residue RMSF flexibility curves, and quantum DFT properties.
  - Implemented `MolecularDynamicsEngine` in `packages/research/src/research/molecular_dynamics_engine.py`:
    - All-atom Velocity Verlet trajectory simulator generating standard PDB multi-model frames with thermal noise and harmonic atomic oscillations.
    - Asymptotic Backbone C$\alpha$ RMSD convergence profiling and equilibrium plateau detection ($\tau \sim 1.45 \text{ \AA}$).
    - Per-residue Root Mean Square Fluctuation (RMSF) dynamic flexibility mapping with flexible loop gating detection.
    - Quantum Density Functional Theory (DFT B3LYP/6-31G*) electronic orbital calculation (HOMO/LUMO levels, bandgap energy $\Delta E$, dipole moment, chemical hardness $\eta$, and Mulliken charges).
  - Implemented REST API routes in `apps/api/src/api/routes/molecular_dynamics.py`:
    - `POST /api/v1/md/simulate`: Execute all-atom MD trajectory with quantum DFT analysis.
    - `GET /api/v1/md/simulations`: List simulations with summary stats and bandgaps.
    - `GET /api/v1/md/simulations/{id}`: Detailed simulation inspection with full trajectory frames and fluctuations.
    - `GET /api/v1/md/simulations/{id}/frames/{frame_index}`: Fetch single coordinate snapshot.
    - `GET /api/v1/md/simulations/{id}/export-trajectory`: Download concatenated multi-model PDB trajectory file.
  - Created interactive Molecular Dynamics & Quantum Chemistry Studio in `apps/web/src/pages/MolecularDynamicsPage.tsx`:
    - 3D Animated Canvas Trajectory Time-Lapse Player with Play/Pause, speed control ($0.5\times - 2.0\times$), time scrubber slider, and dynamic flexibility/structure color coding.
    - Live simulation telemetry (Instantaneous potential energy, temperature, RMSD, timestep).
    - RMSD & Thermodynamic Equilibrium line chart with convergence plateau reference.
    - Per-Residue RMSF Flexibility bar chart with high-flexibility loop badges.
    - Quantum Chemistry & DFT Orbitals Studio with HOMO/LUMO level diagrams, $\Delta E$ bandgap indicator, and reactivity indexes.
    - Frame Snapshots table and Multi-Model PDB export.
  - Mounted `/dynamics` route in `App.tsx` and added `MD Trajectory & Quantum` navigation link with `Atom` icon in `Layout.tsx`.
  - Added unit and integration test suites in `packages/database/tests/test_molecular_dynamics_repo.py`, `packages/research/tests/test_molecular_dynamics_engine.py`, and `apps/api/tests/test_molecular_dynamics_api.py` (404/404 total tests passing).
  - Updated `scripts/seed_demo_data.py` with 100ns AMBER14SB PCSK9 simulation and B3LYP DFT quantum properties.
  - Formalized **ADR 039** in `docs/decisions.md`.

---

## [2.12.0] - 2026-09-15 (Generation 12: Phase 38 - Autonomous Bio-Molecular Structure & Protein Folding Visualizer)

### Added
- **Phase 38: Autonomous Bio-Molecular Structure & Protein Folding Visualizer**:
  - Implemented database persistence models in `packages/database/src/database/models/molecular.py` (`DBMolecularStructure`, `DBBindingPocket`, `DBDockingPose`, `DBMutationStability`) with dialect-safe `GUID()`, JSONB variants, cascade relations, and timezone-aware timestamps.
  - Implemented `MolecularStructureRepository` in `packages/database/src/database/repositories/molecular_repo.py` supporting 3D structure creation, active binding pocket management, in-silico ligand docking poses, and mutational stability scan queries.
  - Implemented `StructurePredictionEngine` in `packages/research/src/research/structure_engine.py`:
    - Generates standard PDB coordinate streams for AlphaFold3 / ESMFold predictions with per-residue pLDDT confidence embedded in the B-factor column.
    - Druggable catalytic pocket and cavity detection with volume ($\text{Å}^3$) and surface area ($\text{Å}^2$) calculation.
    - In-silico ligand docking simulator (AutoDock-Vina / DiffDock proxy) computing binding affinity ($\Delta G$), RMSD, and hydrogen bonding.
    - Thermodynamic folding free energy scan ($\Delta\Delta G$ in $\text{kcal/mol}$) for point mutations with pathogenic classification.
  - Implemented REST API routes in `apps/api/src/api/routes/molecular.py`:
    - `POST /api/v1/molecular/predict`: Predict 3D protein structure and binding pockets.
    - `GET /api/v1/molecular/structures`: List structures filtered by user/workspace/project/uniprot.
    - `GET /api/v1/molecular/structures/{id}`: Detailed structure inspection with pockets, docking poses, and mutations.
    - `POST /api/v1/molecular/structures/{id}/dock`: Execute in-silico ligand docking.
    - `POST /api/v1/molecular/structures/{id}/mutate`: Run mutational stability scan.
    - `GET /api/v1/molecular/structures/{id}/export-pdb`: Download PDB coordinate file.
  - Created interactive Bio-Molecular Structure Studio in `apps/web/src/pages/MolecularStructurePage.tsx`:
    - Interactive 3D Canvas visualizer with ribbon/helix rendering and animated rotation.
    - pLDDT confidence spectrum color scale (Very High $>90$, Confident $70-90$, Low $50-70$, Disordered $<50$).
    - Binding Pocket Explorer with druggability scores and active site residues.
    - In-silico Ligand Docking Studio with binding affinities, RMSD, and hydrogen bonds.
    - $\Delta\Delta G$ Mutational Stability Scanner with pathogenic hotspot warnings.
    - PDB Export & Raw Sequence inspect viewer.
  - Mounted `/molecular` route in `App.tsx` and added `Bio-Molecular Structure` navigation link with `Dna` icon in `Layout.tsx`.
  - Added test suites in `packages/database/tests/test_molecular_repo.py`, `packages/research/tests/test_structure_engine.py`, and `apps/api/tests/test_molecular_api.py` (399/399 total tests passing).
  - Updated `scripts/seed_demo_data.py` with AlphaFold3 PCSK9 & Cas9_Sp structural models.
  - Formalized **ADR 038** in `docs/decisions.md`.

---

## [2.11.0] - 2026-09-15 (Generation 11: Phase 37 - Autonomous Laboratory Automation & Robotic Protocol Generator)

### Added
- **Phase 37: Autonomous Laboratory Automation & Robotic Protocol Generator**:
  - Implemented database models in `packages/database/src/database/models/lab_automation.py` (`DBRoboticProtocol`, `DBLabwareSlot`, `DBLiquidTransferStep`, `DBRoboticExecutionTrace`) with dialect-safe `GUID()`, JSONB variants, cascade relations, and timezone-aware timestamps.
  - Implemented `LabAutomationRepository` in `packages/database/src/database/repositories/lab_automation_repo.py` supporting protocol creation, 12-slot deck layout allocation, atomic pipetting transfer steps, execution trace logging, and multi-tenant filtering.
  - Implemented `RoboticProtocolCompiler` in `packages/research/src/research/robotic_protocol_compiler.py`:
    - Generates production-grade Opentrons Protocol API v2 Python code with metadata, hardware requirements (`OT-2` / `Flex`, API `2.15`), and `run(protocol: protocol_api.ProtocolContext)`.
    - Generates universal PyLabRobot Python automation scripts.
    - Generates standard Autoprotocol JSON specifications for cloud biofoundries.
    - Deterministic deck simulation with reagent volume tracking, pipette capacity validation, liquid class speed adjustments (`aqueous`, `viscous_glycerol`, `volatile_ethanol`), liquid waste calculation, and 3D gantry collision detection for tall labware.
  - Implemented REST API routes in `apps/api/src/api/routes/lab_automation.py`:
    - `POST /api/v1/lab/protocols/compile`: Autonomous compilation, virtual collision check, and protocol persistence.
    - `GET /api/v1/lab/protocols`: List robotic protocols filtered by user/workspace/project/platform.
    - `GET /api/v1/lab/protocols/{id}`: Detailed protocol retrieval with slots, steps, and simulation traces.
    - `POST /api/v1/lab/protocols/{id}/simulate`: Dynamic simulation of custom pipetting sequences.
    - `GET /api/v1/lab/protocols/{id}/export-code`: Multi-format robot code export (`opentrons_python`, `pylabrobot`, `autoprotocol`).
  - Created interactive Robotic Lab Automation Studio in `apps/web/src/pages/LabAutomationPage.tsx`:
    - Interactive 12-Slot Deck Grid Visualizer with slot selection and reagent capacity monitoring.
    - Microfluidic pipetting transfer steps table with liquid class badges.
    - Physics & Collision Telemetry with spatial warning cards and step execution log.
    - Executable code viewer with copy and download utilities.
  - Mounted `/lab` route in `App.tsx` and added `Robotic Lab Automation` navigation link with `Bot` icon in `Layout.tsx`.
  - Added test suites in `packages/database/tests/test_lab_automation_repo.py`, `packages/research/tests/test_robotic_protocol_compiler.py`, and `apps/api/tests/test_lab_automation_api.py` (392/392 total tests passing).
  - Updated `scripts/seed_demo_data.py` with full lab automation protocol demo data.
  - Formalized **ADR 037** in `docs/decisions.md`.

---

## [2.10.0] - 2026-09-15 (Generation 10: Phase 36 - Autonomous Clinical Trial Protocol & Drug Repurposing Engine + Official SDKs + Demo Seeder)

### Added
- **Phase 36: Autonomous Clinical Trial Protocol & Drug Repurposing Engine**:
  - Implemented database models in `packages/database/src/database/models/clinical.py` (`DBClinicalProtocol`, `DBCohortCriterion`, `DBDrugCandidate`, `DBRegulatoryPackage`) with dialect-safe `GUID()`, JSONB variants, cascade relations, and timezone-aware timestamps.
  - Implemented `ClinicalRepository` in `packages/database/src/database/repositories/clinical_repo.py` supporting protocol creation, PICO cohort criteria management, drug repositioning screens, and eCTD regulatory package generation.
  - Implemented `ClinicalTrialEngine` in `packages/research/src/research/clinical_trial_engine.py`:
    - Protocol synthesizer evaluating disease indication, investigational modality, and target mechanisms.
    - PICO structured cohort eligibility generator with standard LOINC clinical lab assay codes.
    - Molecular target-affinity drug repositioning screen ($K_d$ nanomolar affinities, bioavailability %, and toxicity risk scores).
    - eCTD FDA IND / EMA CTD electronic regulatory compliance checker and submission checklists.
  - Implemented REST API routes in `apps/api/src/api/routes/clinical.py`:
    - `POST /api/v1/clinical/protocols/generate`: Autonomous protocol generation and multi-module persistence.
    - `GET /api/v1/clinical/protocols`: List protocols filtered by user/workspace/project.
    - `GET /api/v1/clinical/protocols/{id}`: Detailed protocol inspection with criteria, candidates, and regulatory packages.
    - `POST /api/v1/clinical/protocols/{id}/criteria`: Add custom PICO eligibility criteria.
    - `POST /api/v1/clinical/protocols/{id}/regulatory-package`: Generate eCTD IND compliance package.
  - Created interactive Clinical Trials Studio in `apps/web/src/pages/ClinicalTrialsPage.tsx`:
    - Protocol Synthesizer & Active Protocols Catalog.
    - Planned Cohort, Study Duration, Adverse Risk, and Molecular Target metrics grid.
    - Primary & Secondary Endpoints view.
    - Interactive Tabbed Explorer (PICO Cohort Criteria, Drug Repurposing Screen, FDA IND Dossier).
  - Mounted `/clinical` route in `App.tsx` and added `Clinical Trials & Repurposing` navigation link with `HeartPulse` icon in `Layout.tsx`.
  - Added test suites in `packages/database/tests/test_clinical_repo.py`, `packages/research/tests/test_clinical_trial_engine.py`, and `apps/api/tests/test_clinical_api.py`.
  - Formalized **ADR 036** in `docs/decisions.md`.
- **Official Developer Platform SDKs**:
  - Python async SDK (`ai-research-os` in `packages/sdk-python/ai_research_os`) with `AIResearchClient`, research job submission, polling helpers, document ingestion, usage tracking, and Pydantic models.
  - TypeScript SDK (`apps/web/src/sdk/client.ts`) with typed methods, SSE/WebSocket subscription handlers, and token auth.
- **Production Demo Data Seeder**:
  - Comprehensive seed script (`scripts/seed_demo_data.py`) spanning all 36 platform studios with the flagship project *"Targeted CRISPR-Cas9 Epigenetic Editing via Lipid Nanoparticle Delivery for Monogenic Hepatopathies"*.
- **GENERATION 10 COMPLETED**: Phase 36, Developer Platform SDKs, and Demo Seeder are 100% complete and verified!

---

## [2.9.0] - 2026-09-14 (Generation 9 Milestone 1: Phase 35 - Autonomous Scientific Grant & Research Funding Proposal Synthesizer)

### Added
- **Phase 35: Autonomous Scientific Grant & Research Funding Proposal Synthesizer**:
  - Implemented database models in `packages/database/src/database/models/grant_proposal.py` (`DBGrantProposal`, `DBGrantSpecificAim`, `DBGrantBudgetItem`, `DBGrantReviewScorecard`) with dialect-safe `GUID()`, JSONB variants, cascade relations, and timezone-aware timestamps.
  - Implemented `GrantProposalRepository` in `packages/database/src/database/repositories/grant_proposal_repo.py` supporting proposal lifecycle, specific aims tracking, multi-year budget itemization, mock review scorecard recording, and platform grant metrics (`get_grant_metrics`).
  - Implemented Grant Proposal Synthesizer Engine in `packages/research/src/research/grants/synthesizer.py`:
    - `InstitutionalBudgetCalculator.calculate_multiyear_budget`: Computes institutional multi-year budgets including PI effort, postdoc/student salaries, fringe benefits (28.5%), annual cost escalation (3%), Modified Total Direct Costs (MTDC), and Facilities & Administrative (F&A) indirect cost rates (52%).
    - `GrantProposalSynthesizer.synthesize_proposal_narratives`: Generates Specific Aims, Executive Abstract, Significance, Innovation, Approach, and Preliminary Data narratives for NIH (R01/R21), NSF (CAREER), and Horizon Europe grants.
    - `GrantProposalSynthesizer.conduct_mock_study_section_review`: Simulates study section peer review panels with 1.0 (exceptional) to 9.0 (poor) scoring, percentile rankings, critique strengths/weaknesses, and funding recommendations.
    - `GrantProposalSynthesizer.export_proposal_latex`: Generates complete, compilable LaTeX scientific grant proposals with formal section hierarchies and itemized financial tables.
  - Implemented REST API routes in `apps/api/src/api/routes/grant_proposals.py`:
    - `POST /api/v1/grants/proposals`: Create grant proposal project and synthesize baseline aims and budget.
    - `GET /api/v1/grants/metrics`: Query platform grant funding metrics.
    - `GET /api/v1/grants/proposals`: List grant proposals.
    - `GET /api/v1/grants/proposals/{proposal_id}`: Fetch complete proposal with aims, budget items, and mock review scorecards.
    - `POST /api/v1/grants/proposals/{proposal_id}/synthesize-aims`: Synthesize Specific Aims from research topic.
    - `POST /api/v1/grants/proposals/{proposal_id}/calculate-budget`: Recalculate multi-year institutional budget.
    - `POST /api/v1/grants/proposals/{proposal_id}/mock-review`: Run autonomous study section peer review simulation.
    - `GET /api/v1/grants/proposals/{proposal_id}/export-latex`: Export proposal as compilable LaTeX document.
    - `DELETE /api/v1/grants/proposals/{proposal_id}`: Delete proposal.
  - Created interactive Grant Proposal Studio in `apps/web/src/pages/GrantProposalStudioPage.tsx`:
    - Proposal Catalog & Metrics Overview (`Total Active Proposals`, `Total Funding Pipeline`, `Mean Impact Score`, `High Priority Percentile`).
    - Specific Aims Interactive Editor with hypothesis, experimental design, milestones, and effort allocations.
    - Multi-Year Institutional Budget Calculator with real-time MTDC breakdown and indirect cost estimation.
    - Mock Study Section Review Scorecard with 1.0-9.0 criterion ratings, critique strengths/weaknesses, and fundability badge.
    - LaTeX Exporter with one-click copy and download functionality.
  - Mounted `/grants` route in `App.tsx` and added `Grant Proposals` navigation link with `Landmark` icon in `Layout.tsx`.
  - Added test suites in `packages/database/tests/test_grant_proposal_repo.py`, `packages/research/tests/test_grant_proposal_synthesizer.py`, and `apps/api/tests/test_grant_proposals_api.py`.
  - Formalized **ADR 035** (Autonomous Scientific Grant Proposal Synthesizer, Institutional Budget Calculation, and Mock Study Section Peer Review Engine).
  - **GENERATION 9 MILESTONE 1 COMPLETED**: Phase 35 is 100% complete, verified, and active!

---

## [2.8.0] - 2026-09-14 (Generation 8 Milestone 4: Phase 34 - Autonomous Patent Landscape Analysis & Prior Art Search Engine)

### Added
- **Phase 34: Autonomous Patent Landscape Analysis & Prior Art Search Engine**:
  - Implemented database models in `packages/database/src/database/models/patent.py` (`DBPatentCorpus`, `DBPatentDocument`, `DBPatentClaim`, `DBPriorArtEvaluation`, `DBFreedomToOperateReport`) with dialect-safe `GUID()`, JSONB variants, cascade relations, and timezone-aware timestamps.
  - Implemented `PatentRepository` in `packages/database/src/database/repositories/patent_repo.py` supporting corpus lifecycle, patent/claim indexing, prior art evaluations, FTO clearance reporting, and platform patent metrics (`get_patent_metrics`).
  - Implemented Patent Prior Art Engine in `packages/research/src/research/patents/prior_art.py`:
    - `PatentPriorArtEngine.decompose_claim_limitations`: Decomposes patent claims into preamble, transition, and numbered atomic limitations.
    - `PatentPriorArtEngine.evaluate_prior_art_anticipation`: Evaluates 35 U.S.C. 102 anticipation and 103 obviousness against prior art citations with limitation-by-limitation claim charts and design-around mitigations.
    - `PatentPriorArtEngine.generate_fto_assessment`: Synthesizes Freedom-to-Operate clearance scores, identifies high/medium risk claims, and maps white-space innovation opportunities.
    - `PatentPriorArtEngine.synthesize_baseline_corpus`: Synthesizes structured baseline patent assets conforming to USPTO/EPO/WIPO specifications.
  - Implemented REST API routes in `apps/api/src/api/routes/patents.py`:
    - `POST /api/v1/patents/corpora`: Create patent landscape study and index baseline prior art patents.
    - `GET /api/v1/patents/metrics`: Query platform patent KPIs.
    - `GET /api/v1/patents/corpora`: List patent landscape corpora.
    - `GET /api/v1/patents/corpora/{corpus_id}`: Fetch complete corpus with patents, claims, evaluations, and FTO reports.
    - `POST /api/v1/patents/corpora/{corpus_id}/evaluate-claim`: Run 102/103 prior art evaluation against target claim.
    - `POST /api/v1/patents/corpora/{corpus_id}/fto-report`: Generate Freedom to Operate clearance report and white-space map.
    - `DELETE /api/v1/patents/corpora/{corpus_id}`: Delete corpus.
  - Created interactive Patent Landscape Studio in `apps/web/src/pages/PatentLandscapePage.tsx`:
    - Patent Landscape Explorer with CPC classifications and global jurisdiction filters (`USPTO`, `EPO`, `WIPO`).
    - Interactive 35 U.S.C. 102/103 Claim Chart Studio with atomic limitation breakdown and color-coded status badges (`Anticipated (102)`, `Obvious Variant (103)`, `Novel Distinction`).
    - Freedom to Operate Clearance Gauge and White-Space Innovation Opportunities Studio.
    - New Landscape Study Creator Modal.
  - Mounted `/patents` route in `App.tsx` and added `Patent Landscape` navigation link with `Scale` icon in `Layout.tsx`.
  - Added test suites in `packages/database/tests/test_patent_repo.py`, `packages/research/tests/test_patent_prior_art.py`, and `apps/api/tests/test_patents_api.py`.
  - Formalized **ADR 034** (Autonomous Patent Landscape Analysis, 35 U.S.C. 102/103 Claim Charts, and Freedom-to-Operate (FTO) Engine).
  - **GENERATION 8 MILESTONE COMPLETED**: Generation 8 (Phases 31, 32, 33, 34) is 100% complete, tested, and active!

---

## [2.7.0] - 2026-09-14 (Generation 8 Milestone 3: Phase 33 - Synthetic Instruction Dataset Generation & Active Learning Engine)

### Added
- **Phase 33: Synthetic Instruction Dataset Generation & Active Learning Engine**:
  - Implemented database models in `packages/database/src/database/models/dataset_synthesis.py` (`DBSyntheticDataset`, `DBInstructionSample`, `DBAlignmentExport`) with dialect-safe `GUID()`, JSONB variants, cascade relations, and timezone-aware timestamps.
  - Implemented `DatasetSynthesisRepository` in `packages/database/src/database/repositories/dataset_synthesis_repo.py` supporting dataset lifecycle, sample batch addition, active learning curation updates, export recording, and platform synthesis metrics (`get_synthesis_metrics`).
  - Implemented Instruction Synthesizer Engine in `packages/research/src/research/datasets/synthesizer.py`:
    - `InstructionDatasetSynthesizer.synthesize_from_research_findings`: Generates high-entropy instruction-response samples or DPO pairs from research findings.
    - `InstructionDatasetSynthesizer.evolve_instruction`: Evol-Instruct prompt mutator supporting `in_depth_expansion`, `in_breadth_variation`, `constraint_hardening`, `adversarial_redteaming`, and `cot_decomposition`.
    - `InstructionDatasetSynthesizer.format_dataset`: Converts samples to Alpaca SFT, ShareGPT Multi-Turn, DPO Preference Pairs, or CoT formats.
    - `InstructionDatasetSynthesizer.calculate_quality_metrics`: Deterministic quality, toxicity, hallucination risk, and SHA-256 deduplication hashing.
  - Implemented REST API routes in `apps/api/src/api/routes/dataset_synthesis.py`:
    - `POST /api/v1/datasets/synthesize`: Synthesize instruction tuning dataset from research findings.
    - `GET /api/v1/datasets/metrics`: Query platform dataset metrics.
    - `GET /api/v1/datasets`: List synthetic datasets.
    - `GET /api/v1/datasets/{dataset_id}`: Fetch complete dataset with samples and export history.
    - `PATCH /api/v1/datasets/{dataset_id}/samples/{sample_id}`: Human/Active-learning curation.
    - `POST /api/v1/datasets/{dataset_id}/export`: Export dataset into standardized fine-tuning JSONL format.
    - `DELETE /api/v1/datasets/{dataset_id}`: Delete dataset.
  - Created interactive Dataset Synthesis Studio in `apps/web/src/pages/DatasetSynthesisPage.tsx`:
    - Dataset Catalog & Format Selector (`Alpaca SFT`, `ShareGPT`, `DPO Preference Pairs`, `Chain-of-Thought`).
    - Instruction Sample Inspector & Active Learning Curation Studio with side-by-side chosen vs. rejected responses and CoT reasoning traces.
    - Evol-Instruct Strategy badges and quality score gauges.
    - One-click Standardized Alignment JSONL Exporter with live clipboard copy and file download.
  - Mounted `/datasets` route in `App.tsx` and added `Dataset Synthesis` navigation link with `Database` icon in `Layout.tsx`.
  - Added test suites in `packages/database/tests/test_dataset_synthesis_repo.py`, `packages/research/tests/test_dataset_synthesizer.py`, and `apps/api/tests/test_dataset_synthesis_api.py`.
  - Formalized **ADR 033** (Synthetic Instruction Dataset Generation, Evol-Instruct Mutations, and Active Learning Alignment Engine).
  - **MILESTONE COMPLETED**: Generation 8 Milestone 3 (Phase 33) is 100% complete, tested, and active!

---

## [2.6.0] - 2026-09-14 (Generation 8 Milestone 2: Phase 32 - Real-Time Collaborative Research Canvas & Visual Ideation Studio)

### Added
- **Phase 32: Real-Time Multi-Agent Collaborative Research Canvas & Visual Ideation Studio**:
  - Implemented database models in `packages/database/src/database/models/canvas.py` (`DBCanvasBoard`, `DBCanvasNode`, `DBCanvasEdge`) with dialect-safe `GUID()`, JSONB variants, cascade relations, and timezone-aware timestamps.
  - Implemented `CanvasRepository` in `packages/database/src/database/repositories/canvas_repo.py` supporting board lifecycle, node/edge additions, coordinate updates, batch additions, metrics (`get_canvas_metrics`), and cascade deletion.
  - Implemented Research Canvas Engine in `packages/research/src/research/canvas/ideation.py`:
    - `CanvasIdeationEngine.generate_canvas_from_research`: Synthesizes structured 2D topological DAG layouts from findings, evidence, and conclusions.
    - `CanvasIdeationEngine.synthesize_agent_brainstorm_nodes`: Generates multi-agent brainstorming nodes (counter-hypotheses and orthogonal inquiries).
    - `CanvasIdeationEngine.detect_canvas_clusters`: Computes connected subgraph clusters across canvas nodes.
  - Implemented REST API routes in `apps/api/src/api/routes/canvas.py`:
    - `POST /api/v1/canvas/boards`: Create research canvas board.
    - `GET /api/v1/canvas/metrics`: Query platform canvas & node metrics.
    - `GET /api/v1/canvas/boards`: List canvas boards.
    - `GET /api/v1/canvas/boards/{board_id}`: Fetch complete board with nodes and edges.
    - `POST /api/v1/canvas/boards/{board_id}/generate`: Auto-generate 2D DAG from research findings.
    - `POST /api/v1/canvas/boards/{board_id}/nodes`: Add visual research node.
    - `PATCH /api/v1/canvas/boards/{board_id}/nodes/{node_id}`: Update node position and status.
    - `POST /api/v1/canvas/boards/{board_id}/edges`: Add relational edge.
    - `POST /api/v1/canvas/boards/{board_id}/brainstorm`: Trigger AI agent brainstorming expansion.
    - `DELETE /api/v1/canvas/boards/{board_id}`: Delete board.
  - Created interactive Research Canvas Studio in `apps/web/src/pages/ResearchCanvasPage.tsx`:
    - Infinite 2D interactive canvas viewport with smooth zooming, panning, and customizable background grid (dots, lines, crosses, clean).
    - Visual node-graph renderer with type-specific color accents, status badges, drag/drop interaction, and connecting SVG relation lines.
    - AI Brainstorming Trigger and Auto-Generate from Research dossier modal.
    - Node detail drawer with confidence scores, relations, and metadata.
  - Mounted `/canvas` route in `App.tsx` and added `Research Canvas` navigation link with `Network` icon in `Layout.tsx`.
  - Added test suites in `packages/database/tests/test_canvas_repo.py`, `packages/research/tests/test_canvas_ideation.py`, and `apps/api/tests/test_canvas_api.py`.
  - Formalized **ADR 032** (Real-Time Multi-Agent Collaborative Research Canvas & Visual Ideation Studio).
  - **MILESTONE COMPLETED**: Generation 8 Milestone 2 (Phase 32) is 100% complete, tested, and active!

---

## [2.5.0] - 2026-09-14 (Generation 8 Milestone 1: Phase 31 - Autonomous Scientific Peer Review & Journal Publishing Pipeline)

### Added
- **Phase 31: Autonomous Multi-Agent Blinded Peer Review & Academic Publishing Pipeline**:
  - Implemented database models in `packages/database/src/database/models/peer_review.py` (`DBPeerReviewManuscript`, `DBPeerReviewReport`, `DBManuscriptRevision`) with dialect-safe `GUID()`, JSONB variants, and timezone-aware timestamps.
  - Implemented `PeerReviewRepository` in `packages/database/src/database/repositories/peer_review_repo.py` supporting manuscript submission, referee reports saving, composite score aggregation, author revisions, camera-ready publishing, and platform metrics (`get_peer_review_metrics`).
  - Implemented Multi-Agent Peer Review and Publishing Engine in `packages/research/src/research/publishing/peer_review.py`:
    - `PeerReviewEngine.evaluate_manuscript`: Multi-agent double-blind evaluation simulating 3 specialized referee personas (`methodology_critic`, `statistical_auditor`, `domain_specialist`) with weighted metrics across originality, methodological rigor, empirical soundness, and clarity.
    - `PublicationFormatter`: Generates camera-ready academic preprints (LaTeX source conforming to Nature / IEEE / ACM guidelines), BibTeX citation blocks, and canonical DOI identifiers.
    - `AuthorRebuttalGenerator`: Synthesizes point-by-point author rebuttal letters addressing referee critique items.
  - Implemented REST API routes in `apps/api/src/api/routes/peer_review.py`:
    - `POST /api/v1/publishing/manuscripts`: Submit manuscript for peer review.
    - `GET /api/v1/publishing/metrics`: Query platform peer review and publication statistics.
    - `GET /api/v1/publishing/manuscripts`: List manuscripts with filters.
    - `GET /api/v1/publishing/manuscripts/{id}`: Fetch manuscript details with referee reports and author revisions.
    - `POST /api/v1/publishing/manuscripts/{id}/review`: Trigger multi-agent double-blind peer review simulation.
    - `POST /api/v1/publishing/manuscripts/{id}/revisions`: Submit author rebuttal and revision round.
    - `POST /api/v1/publishing/manuscripts/{id}/publish`: Generate camera-ready preprint, BibTeX, and formal DOI.
    - `DELETE /api/v1/publishing/manuscripts/{id}`: Delete manuscript.
  - Created interactive Peer Review & Publishing Studio in `apps/web/src/pages/PeerReviewPage.tsx`:
    - Blind Referee Panel & Scorecard (radar/bar breakdowns across Originality, Methodological Rigor, Empirical Soundness, Clarity, detailed comments and recommendations).
    - Author Rebuttal & Revision Studio (rebuttal letters, point-by-point response tracking).
    - Camera-Ready Preprint & Publishing Studio (LaTeX source viewer, BibTeX copy block, DOI badge).
    - Submit Manuscript modal with multi-venue format selector (`Nature`, `IEEE`, `ACM`, `arXiv`).
  - Mounted `/publishing` route in `App.tsx` and added `Peer Review & Publishing` navigation link with `Award` icon in `Layout.tsx`.
  - Added test suites in `packages/database/tests/test_peer_review_repo.py`, `packages/research/tests/test_peer_review_engine.py`, and `apps/api/tests/test_peer_review_api.py`.
  - Formalized **ADR 031** (Autonomous Multi-Agent Blinded Peer Review, Author Rebuttals, and Camera-Ready Academic Preprint Publishing Pipeline).
  - **MILESTONE COMPLETED**: Generation 8 Milestone 1 (Phase 31) is 100% complete, tested, and active!

---

## [2.4.0] - 2026-09-14 (Generation 7 Milestone 4: Phase 30 - Multimodal Scientific Presentation & Executive Podcasting Briefing Generator)

### Added
- **Phase 30: Multimodal Scientific Presentation Decks & Multi-Speaker Executive Podcasting Briefing Generator**:
  - Implemented database models in `packages/database/src/database/models/presentation.py` (`DBSynthesisPresentation`, `DBPresentationSlide`, `DBPodcastBriefing`) with dialect-safe `GUID()`, JSONB variants, and timezone-aware timestamps.
  - Implemented `PresentationRepository` in `packages/database/src/database/repositories/presentation_repo.py` supporting presentation lifecycle (`create_presentation`, `get_presentation`, `list_presentations`, `delete_presentation`), slide operations (`save_slides`, `get_slides`), podcast briefings (`create_podcast_briefing`, `get_podcast_briefing`, `list_podcast_briefings`), and platform-wide presentation metrics (`get_presentation_metrics`).
  - Implemented `PresentationGenerator` and `PodcastBriefingSynthesizer` in `packages/research/src/research/presentation/synthesizer.py`:
    - `PresentationGenerator.generate_presentation(title, topic, summary, findings, target_audience, slide_count)`: Generates structured scientific slide decks with layouts (`title_slide`, `key_findings`, `architecture_flow`, `comparative_analysis`, `conclusion_next_steps`), bullet assertions, visual cards, charts, and detailed speaker script notes.
    - `PodcastBriefingSynthesizer.generate_podcast(title, topic, key_points, findings, style, target_duration_minutes)`: Generates structured multi-speaker dialogue scripts (`Host (Alex)` & `Domain Specialist (Dr. Rowan)`) with tone cues (`engaging_inquisitive`, `authoritative_analytical`, `balanced_synthesis`), duration calculation, and automated chapter timestamps.
  - Implemented REST API routes in `apps/api/src/api/routes/presentations.py`:
    - `POST /api/v1/presentations/generate`: Synthesize structured presentation slide deck.
    - `GET /api/v1/presentations`: List synthesized presentations.
    - `GET /api/v1/presentations/{id}`: Fetch presentation details with full slide deck.
    - `POST /api/v1/presentations/podcasts/generate`: Synthesize multi-speaker podcast briefing.
    - `GET /api/v1/presentations/podcasts`: List generated podcast briefings.
    - `GET /api/v1/presentations/podcasts/{id}`: Fetch podcast briefing dialogue.
    - `GET /api/v1/presentations/metrics`: Query platform presentation and podcast metrics.
    - `DELETE /api/v1/presentations/{id}`: Delete presentation deck.
  - Created interactive Multimodal Presentation & Podcast Studio in `apps/web/src/pages/PresentationStudioPage.tsx`:
    - Slide Deck Presenter tab (live slide stage with full-screen toggle, layout-aware card rendering, slide navigation bar, and expandable presenter speaker notes).
    - Slide List & Hierarchy tab (compact grid overview of all deck slides with bullet points, visuals, and timing).
    - Executive Podcast Player & Transcript tab (audio player simulation, multi-speaker dialogue view with speaker avatar badges, duration/word-count badges, and timestamped chapter markers).
    - Synthesize New Deck & Generate Podcast modals.
  - Mounted `/presentations` route in `App.tsx` and added `Presentation Studio` navigation link with `Tv` icon in `Layout.tsx`.
  - Added test suites in `packages/database/tests/test_presentation_repo.py`, `packages/research/tests/test_presentation_synthesizer.py`, and `apps/api/tests/test_presentation_api.py`.
  - Formalized **ADR 030** (Multimodal Scientific Presentation Decks and Multi-Speaker Executive Podcasting Briefing Generator).
  - **MILESTONE COMPLETED**: Generation 7 Milestone 4 (Phase 30) is 100% complete, tested, and active!

---

## [2.3.0] - 2026-09-14 (Generation 7 Milestone 3: Phase 29 - In-Silico Experimentation, Computational Reproducibility & Code Verification)

### Added
- **Phase 29: In-Silico Experimentation, Computational Reproducibility & Empirical Claim Verification Engine**:
  - Implemented database models in `packages/database/src/database/models/reproducibility.py` (`DBExperimentProtocol`, `DBReproducibilityRun`, `DBClaimVerificationTrace`) with dialect-safe `GUID()`, JSONB variants, and timezone-aware timestamps.
  - Implemented `ReproducibilityRepository` in `packages/database/src/database/repositories/reproducibility_repo.py` supporting computational protocol lifecycle (`create_protocol`, `get_protocol`, `list_protocols`, `update_protocol_status`, `delete_protocol`), in-silico execution runs (`record_reproducibility_run`, `get_run`, `list_runs`), claim verification traces (`record_verification_trace`, `list_verification_traces`), and aggregate platform metrics (`get_reproducibility_metrics`).
  - Implemented `ReproducibilityEngine` in `packages/research/src/research/reproducibility/engine.py`:
    - `validate_code_ast(code)`: AST tree security parser screening against prohibited modules (`os`, `sys`, `subprocess`, `socket`, `requests`, `eval`, `exec`, `open`).
    - `execute_protocol(code, parameters)`: Sandboxed runtime scope with pre-loaded mathematical modules (`math`, `random`, `statistics`), stdout terminal interceptor, and numerical output metric extraction.
    - `verify_claims(claimed_metrics, reproduced_metrics, tolerance)`: Relative delta error calculator ($\delta = \frac{|M_{\text{claimed}} - M_{\text{reproduced}}|}{\max(|M_{\text{claimed}}|, 1e-6)}$), tolerance-based verdict categorization (`reproduced`, `discrepant`, `refuted`, `inconclusive`), and composite reproducibility score $\kappa \in [0.0, 1.0]$.
  - Implemented REST API routes in `apps/api/src/api/routes/reproducibility.py`:
    - `POST /api/v1/reproducibility/protocols`: Register computational protocol.
    - `GET /api/v1/reproducibility/protocols`: List protocols with filtering.
    - `GET /api/v1/reproducibility/protocols/{id}`: Fetch protocol with runs and claim verification traces.
    - `POST /api/v1/reproducibility/protocols/{id}/execute`: Trigger in-silico simulation run and automated claim verification.
    - `GET /api/v1/reproducibility/metrics`: Query platform reproducibility metrics.
    - `DELETE /api/v1/reproducibility/protocols/{id}`: Delete protocol.
  - Created interactive In-Silico Experimentation & Reproducibility Studio in `apps/web/src/pages/ReproducibilityPage.tsx`:
    - Protocols & Code Studio tab (protocol selector, paper reference badge, claimed benchmark metrics grid, AST-sandboxed code editor).
    - Simulation Console & Telemetry tab (live stdout terminal output, execution duration gauge, peak heap memory telemetry, computed output metrics grid, re-run trigger).
    - Claim Verification Matrix tab (granular claim vs. reproduced comparison table, relative delta error percentages, tolerance thresholds, and verdict badges).
    - Run History & Scorecard tab (chronological historical runs and composite reproducibility scores).
    - Register Protocol modal with template script.
  - Mounted `/reproducibility` route in `App.tsx` and added `In-Silico Verification` navigation link with `Cpu` icon in `Layout.tsx`.
  - Added test suites in `packages/database/tests/test_reproducibility_repo.py`, `packages/research/tests/test_reproducibility_engine.py`, and `apps/api/tests/test_reproducibility_api.py`.
  - Formalized **ADR 029** (In-Silico Experimentation, Sandboxed Computational Reproducibility, and Claim Discrepancy Verification).
  - **MILESTONE COMPLETED**: Generation 7 Milestone 3 (Phase 29) is 100% complete, tested, and active!

---

## [2.2.0] - 2026-09-14 (Generation 7 Milestone 2: Phase 28 - Autonomous Systematic Literature Review & PRISMA Meta-Analysis)

### Added
- **Phase 28: Autonomous Systematic Literature Review, PRISMA 2020 Protocol Flow & Quantitative Meta-Analysis**:
  - Implemented database models in `packages/database/src/database/models/literature.py` (`DBLiteratureReview`, `DBSLRCriterion`, `DBSLRStudyCandidate`, `DBMetaAnalysisReport`, `DBRiskOfBiasAssessment`) with dialect-safe `GUID()`, JSONB variants, and timezone-aware timestamps.
  - Implemented `LiteratureRepository` in `packages/database/src/database/repositories/literature_repo.py` supporting SLR review lifecycle (`create_literature_review`, `get_literature_review`, `list_literature_reviews`, `update_review_phase`, `recalculate_review_counts`, `delete_literature_review`), criteria management (`add_criterion`, `list_criteria`), candidate study screening (`add_candidate_studies`, `get_candidate_study`, `update_candidate_screening`, `list_candidate_studies`), Risk of Bias auditing (`save_risk_of_bias`), and quantitative meta-analysis saving (`save_meta_analysis_report`, `get_meta_analysis_report`, `get_slr_metrics`).
  - Implemented deterministic Meta-Analysis & SLR Engine in `packages/research/src/research/literature/meta_analysis.py`:
    - `EffectSizeCalculator`: Deterministic computation of Cohen's $d$, small-sample bias corrected Hedges' $g$, and natural log Odds Ratios with 95% confidence intervals.
    - `HeterogeneityEngine`: Cochrane's $Q$ statistic, degrees of freedom, $I^2$ inconsistency index ($0-100\%$), DerSimonian-Laird between-study variance $\tau^2$, and chi-square approximation $p$-value.
    - `PooledEffectEstimator`: Fixed-effect (Inverse-Variance) and Random-Effects (DerSimonian-Laird) model pooling with coordinates for forest plots.
    - `PRISMAFlowTracker`: 4-box PRISMA 2020 identification, screening, eligibility, and included funnel telemetry with study attrition metrics.
    - `RiskOfBiasEvaluator`: Multi-domain Cochrane RoB 2 / ROBINS-I criteria evaluation across Selection, Confounding, Measurement, and Reporting bias.
    - `SLROrchestrator`: Full SLR review and quantitative meta-analysis synthesis pipeline.
  - Implemented REST API routes in `apps/api/src/api/routes/literature.py`:
    - `POST /api/v1/literature/reviews`: Create new Systematic Literature Review.
    - `GET /api/v1/literature/reviews`: List reviews with workspace/project/phase filtering.
    - `GET /api/v1/literature/reviews/{id}`: Fetch review details with criteria, candidate studies, and meta-analyses.
    - `POST /api/v1/literature/reviews/{id}/criteria`: Add inclusion/exclusion criterion.
    - `POST /api/v1/literature/reviews/{id}/candidates`: Batch add candidate studies.
    - `PATCH /api/v1/literature/reviews/{id}/candidates/{cand_id}`: Screen candidate study and record effect metrics.
    - `POST /api/v1/literature/reviews/{id}/meta-analysis`: Run quantitative meta-analysis calculation.
    - `POST /api/v1/literature/reviews/{id}/risk-of-bias`: Record study Risk of Bias evaluation.
    - `GET /api/v1/literature/reviews/{id}/prisma-flow`: Fetch PRISMA 2020 flow report.
    - `GET /api/v1/literature/metrics`: Query platform SLR metrics.
    - `DELETE /api/v1/literature/reviews/{id}`: Delete SLR and cascade child records.
  - Created interactive Systematic Literature Review & Meta-Analysis Studio in `apps/web/src/pages/LiteratureReviewPage.tsx`:
    - PRISMA 2020 Flow & Overview tab (interactive 4-box flowchart, live attrition rate, review selector, PICO framework breakdown, criteria summary pills).
    - Screening Queue & Triage tab (candidate cards with methodology badges, 1-click Include / Exclude action buttons, exclusion reason taxonomy, sample size / effect size badges).
    - Quantitative Meta-Analysis & Forest Plot Studio (run meta-analysis modal, pooled effect size & 95% CI summary cards, $I^2$ heterogeneity metric, visual Forest Plot with study confidence intervals, weights, and pooled diamond summary).
    - Risk of Bias (RoB 2) Matrix Heatmap tab (domain-level quality table across Selection, Confounding, Measurement, and Reporting bias with color-coded Low Risk / Some Concerns / High Risk badges).
    - Create SLR Review modal with PICO framework fields.
  - Mounted `/literature` route in `App.tsx` and added `Literature Reviews` navigation link with `BookOpenCheck` icon in `Layout.tsx`.
  - Added test suites in `packages/database/tests/test_literature_repo.py`, `packages/research/tests/test_meta_analysis.py`, and `apps/api/tests/test_literature_api.py`.
  - Formalized **ADR 028** (Autonomous Systematic Literature Review, PRISMA 2020 Protocol Flow, and Quantitative Meta-Analysis).
  - **MILESTONE COMPLETED**: Generation 7 Milestone 2 (Phase 28) is 100% complete, tested, and active!

---

## [2.1.0] - 2026-09-13 (Generation 7 Milestone 1: Phase 27 - Adversarial Multi-Agent Debate & Consensus Engine)

### Added
- **Phase 27: Adversarial Multi-Agent Debate, Elo Robustness Scoring & Dialectical Consensus Synthesis**:
  - Implemented database models in `packages/database/src/database/models/debate.py` (`DBAgentDebate`, `DBDebateRound`, `DBDebateConsensus`) with dialect-safe `GUID()`, JSONB variants, and timezone-aware timestamps.
  - Implemented `DebateRepository` in `packages/database/src/database/repositories/debate_repo.py` supporting debate lifecycle (`create_debate`, `get_debate`, `list_debates`, `update_debate_status`, `add_debate_round`, `list_debate_rounds`, `record_consensus`, `get_consensus`, `get_debate_metrics`, `delete_debate`).
  - Implemented specialized debate agents in `packages/agents/src/agents/debate/`:
    - `ProposerAgent`: Affirmative evidence-grounded thesis defense, deduction formulation, citation tracking, and honest concession reporting.
    - `OpposerAgent`: Adversarial counterarguments, edge case stress testing, methodology criticism, and fallacy detection.
    - `ConsensusArbiter`: Impartial round evaluation, argument scoring, critique generation, and dialectical consensus synthesis.
  - Implemented `DebateEngine` in `packages/research/src/research/debate/engine.py` with standard Elo rating shift updates ($\Delta R = K \times (S - E)$ with $K=32.0$), round-by-round orchestration, autonomous full debate runs, and automatic consensus recording.
  - Implemented REST API routes in `apps/api/src/api/routes/debate.py`:
    - `POST /api/v1/debates`: Launch new debate session.
    - `GET /api/v1/debates`: List debates with workspace/project/status filters.
    - `GET /api/v1/debates/{id}`: Retrieve debate with rounds and consensus.
    - `POST /api/v1/debates/{id}/rounds`: Execute next round or full debate run.
    - `GET /api/v1/debates/{id}/rounds`: List chronological round transcripts and citations.
    - `GET /api/v1/debates/{id}/consensus`: Retrieve synthesized consensus.
    - `GET /api/v1/debates/metrics`: Query aggregate debate statistics.
    - `DELETE /api/v1/debates/{id}`: Delete debate and cascade child records.
  - Created interactive Debate Arena Studio in `apps/web/src/pages/DebateArenaPage.tsx`:
    - Active Debates tab (grid of active/concluded debates, Elo rating pills, round counters, launch debate modal).
    - Split-Screen Dialectical Arena Inspector (side-by-side Proposer vs Opposer transcript viewer, claim cards, citations, Arbiter critique card with round winner and Elo delta indicator).
    - Synthesized Consensus Vault tab (high-confidence consensus statement card, accepted empirical claims with confidence bars, refuted claims, mutual concessions, and residual uncertainties).
  - Mounted `/debates` in `App.tsx` and added `Debate Arena` link in `Layout.tsx` with `Swords` icon.
  - Added test suites in `packages/database/tests/test_debate_repo.py`, `packages/research/tests/test_debate_engine.py`, and `apps/api/tests/test_debate_api.py`, achieving 100% pass rate (333/333 tests passing across entire monorepo).
  - Formalized **ADR 027** (Adversarial Multi-Agent Debate, Elo Robustness Scoring, and Dialectical Consensus Synthesis).
  - **MILESTONE COMPLETED**: Generation 7 Milestone 1 is 100% complete, tested, and active!

---

## [2.0.0] - 2026-09-13 (Generation 6 Milestone 4 & 6-Generation Product Roadmap Completion: Phase 26 - Research Automation)

### Added
- **Phase 26: Research Automation, Cron Scheduling, Semantic Diffing & Alerting**:
  - Implemented database models in `packages/database/src/database/models/automation.py` (`DBScheduledResearch`, `DBResearchSweepResult`, `DBAutomationAlert`) with dialect-safe `GUID()`, JSONB variants, and timezone-aware timestamps.
  - Implemented `AutomationRepository` in `packages/database/src/database/repositories/automation_repo.py` supporting schedule CRUD (`create_schedule`, `get_schedule`, `list_schedules`, `update_schedule`, `pause_schedule`, `resume_schedule`, `delete_schedule`), sweep recording (`record_sweep_result`, `list_sweep_results`), alert management (`create_alert`, `list_alerts`, `acknowledge_alert`), and aggregate automation telemetry (`get_automation_metrics`).
  - Implemented `ResearchAutomationEngine` in `packages/research/src/research/automation/engine.py`:
    - `compute_next_run(cron_expression, interval_seconds)`: Robust timestamp calculator supporting 5-field cron parsing and interval frequencies.
    - `detect_novelty(current_claims, prior_claims)`: Semantic claim normalization and diff engine isolating novel and contradictory claims and generating novelty intensity scores $\in [0.0, 1.0]$.
    - `execute_scheduled_sweep(schedule_id)`: Autonomous sweep execution pipeline that retrieves prior findings, calculates novelty, records sweep results, and dispatches in-app and webhook alerts when $\text{novelty} \ge \tau_{\text{novel}}$.
  - Implemented REST API routes in `apps/api/src/api/routes/automation.py`:
    - `POST /api/v1/automation/schedules`: Create recurring research sweeps.
    - `GET /api/v1/automation/schedules`: List research schedules.
    - `GET /api/v1/automation/schedules/{id}`: Fetch schedule details.
    - `PATCH /api/v1/automation/schedules/{id}/pause` & `/resume`: Pause and resume schedules.
    - `DELETE /api/v1/automation/schedules/{id}`: Delete schedules.
    - `POST /api/v1/automation/schedules/{id}/trigger`: Trigger immediate on-demand sweep.
    - `GET /api/v1/automation/schedules/{id}/sweeps`: List historical sweeps and diffs.
    - `GET /api/v1/automation/alerts`: List change detection alerts with unread filtering.
    - `PATCH /api/v1/automation/alerts/{id}/acknowledge`: Mark alert as acknowledged.
    - `GET /api/v1/automation/metrics`: Query aggregate automation metrics.
  - Created interactive Research Automation Studio in `apps/web/src/pages/ResearchAutomationPage.tsx`:
    - Sweeps & Cron Schedules tab (active/paused schedules, countdown badges, instant trigger, pause/resume, and schedule creator modal).
    - Sweep History & Diff Explorer tab (chronological sweep feed, novel/contradictory claim badges, crawl stats, novelty score gauge).
    - Dispatched Alerts & Webhooks tab (unread alert cards, novelty score badges, 1-click acknowledge button, webhook test dispatcher).
  - Mounted `/automation` in `App.tsx` and added `Research Automation` link in `Layout.tsx`.
  - Added test suites in `packages/database/tests/test_automation_repo.py`, `packages/research/tests/test_research_automation.py`, and `apps/api/tests/test_automation_api.py`, achieving 100% pass rate (329/329 tests passing across entire monorepo).
  - Formalized **ADR 026** (Autonomous Research Automation, Cron Scheduling, and Novelty-Triggered Multi-Channel Alerting).
  - **MILESTONE COMPLETED**: All 26 Phases across all 6 Generations are now 100% complete, tested, and production ready!

---

## [1.9.0] - 2026-09-13 (Generation 6 Milestone 3: Phase 25 - Public API & Developer Platform)

### Added
- **Phase 25: Public API Gateway, Developer Platform & SDK Playground**:
  - Implemented secure API key model `DBApiKey` in `packages/database/src/database/models/api_key.py` with `key_prefix` indexing, SHA-256 `key_hash` storage, granular permission scopes (`research:read/write`, `documents:read/write`, `memory:read`, `graph:read`), and rate limit tiers (`free`, `pro`, `enterprise`).
  - Implemented `ApiKeyRepository` in `packages/database/src/database/repositories/api_key_repo.py` supporting constant-time hash authentication, scope enforcement, and sliding 60-second window rate limit enforcement (`check_rate_limit`).
  - Implemented public developer REST API endpoints in `apps/api/src/api/routes/developer.py`:
    - `GET /api/v1/developer/keys`: Lists developer keys with masked previews.
    - `POST /api/v1/developer/keys`: Generates new cryptographically secure API key with one-time plaintext reveal.
    - `GET /api/v1/developer/keys/{id}`: Retrieves specific key metadata.
    - `PATCH /api/v1/developer/keys/{id}/revoke`: Immediately revokes key access.
    - `DELETE /api/v1/developer/keys/{id}`: Permanently deletes API key record.
    - `POST /api/v1/developer/research`: Public endpoint for triggering research via `X-API-Key` header.
    - `GET /api/v1/developer/research/{id}`: Public endpoint for polling research progress and fetching finished reports.
    - `POST /api/v1/developer/documents`: Public endpoint for ingesting text/documents.
    - `GET /api/v1/developer/usage`: Public endpoint for developer token/request analytics.
  - Created interactive Developer Platform Studio in `apps/web/src/pages/DeveloperPlatformPage.tsx` with API Keys Vault, Create Key modal with scope & expiration selector, One-Time Key Reveal modal, Interactive API Playground & SDK generator (cURL, Python `requests`, TypeScript `axios`), and Rate Limits & Quotas breakdown.
  - Mounted `/developer` route in `App.tsx` and added `Developer API` navigation link in `Layout.tsx`.
  - Added test suites in `packages/database/tests/test_api_key_repo.py` and `apps/api/tests/test_developer_api.py`, achieving 100% pass rate.
  - Formalized **ADR 025** (Public API Gateway, SHA-256 Hashed API Keys, and Sliding Window Rate Limiting).

---

## [1.8.0] - 2026-09-13 (Generation 6 Milestone 2: Phase 24 - Production Scale Infrastructure)

### Added
- **Phase 24: Production Infrastructure, Priority Task Queue & Blob Storage Vault**:
  - Implemented asynchronous priority task queue and worker node engine in `packages/research/src/research/workers/task_queue.py` (`AsyncTaskQueue`, `QueuedTask`, `WorkerNode`, `TaskPriority`, and `global_task_queue`) supporting 4 priority levels (`CRITICAL`, `HIGH`, `DEFAULT`, `LOW`), concurrency throttling, retry counters, and task leases.
  - Implemented unified multi-provider object storage client in `packages/shared/src/shared/storage.py` (`ObjectStorageClient`, `StorageBackendType`, `StorageObjectMetadata`) supporting AWS S3, MinIO, and local filesystem backends with presigned URL generation, MD5/SHA-256 checksumming, and aggregate bucket usage telemetry.
  - Implemented database models `DBWorkerNode` and `DBStorageObject` in `packages/database/src/database/models/infrastructure.py` with full PostgreSQL/SQLite parity.
  - Implemented `InfrastructureRepository` in `packages/database/src/database/repositories/infrastructure_repo.py` supporting worker node registration, heartbeat leasing, task assignment, blob recording, and storage usage calculations.
  - Implemented REST API endpoints in `apps/api/src/api/routes/system_infra.py`:
    - `GET /api/v1/system/workers`: Lists cluster worker nodes with heartbeat health.
    - `POST /api/v1/system/workers/heartbeat`: Worker pulse registering CPU/RAM load and active tasks.
    - `GET /api/v1/system/queue/status`: Returns priority queue length, latency, and throughput metrics.
    - `POST /api/v1/system/queue/tasks`: Enqueues research tasks with priority.
    - `GET /api/v1/system/storage/objects`: Queries stored object blobs.
    - `POST /api/v1/system/storage/presigned-url`: Generates secure presigned download/upload links.
    - `GET /api/v1/system/storage/usage`: Computes total byte and object count storage metrics.
  - Created interactive Production Infrastructure Studio in `apps/web/src/pages/ProductionInfrastructurePage.tsx` with Cluster Topology dashboard, Distributed Task Queue manager, S3/MinIO Blob Storage browser, Heartbeat simulator modal, Task enqueue modal, and Presigned URL generator modal.
  - Mounted `/infrastructure` route in `App.tsx` and added `Infrastructure` navigation link in `Layout.tsx`.
  - Added test suites in `packages/research/tests/test_async_task_queue.py`, `packages/shared/tests/test_object_storage.py`, `packages/database/tests/test_infrastructure_repo.py`, and `apps/api/tests/test_system_infra_api.py`, achieving 100% pass rate (319/319 tests passing across monorepo).
  - Formalized **ADR 024** (Distributed Priority Task Queue, Asynchronous Worker Clusters, and S3/MinIO Blob Vault Architecture).

---

## [1.7.0] - 2026-09-13 (Generation 6 Milestone 1: Phase 23 - Enterprise Security & Compliance Platform)

### Added
- **Phase 23: Enterprise Security, KMS Secret Vault & Cryptographic Audit Trails**:
  - Implemented military-grade two-tier envelope encryption engine `KMSEnvelopeEncryption` in `packages/shared/src/shared/kms.py` using PBKDF2-HMAC-SHA256 derived Key Encryption Key (KEK) and ephemeral 256-bit Data Encryption Key (DEK) with AES-256-GCM authenticated ciphertext.
  - Implemented blockchain-like tamper-evident cryptographic SHA-256 audit hash chaining `AuditHashChainer` in `packages/shared/src/shared/kms.py` calculating deterministic hashes linked to preceding records with `verify_chain_integrity()` validation.
  - Implemented database models `DBSecurityAuditLog`, `DBEncryptedSecret`, and `DBSecurityPolicy` in `packages/database/src/database/models/security.py` with full PostgreSQL/SQLite parity.
  - Implemented `SecurityRepository` in `packages/database/src/database/repositories/security_repo.py` supporting hash-chained audit event creation, integrity verification, secret vaulting/revocation, security policy management, and GDPR Article 17 automated cascade data purge (`execute_gdpr_data_purge`).
  - Implemented REST API endpoints in `apps/api/src/api/routes/security.py`:
    - `POST /api/v1/security/audit-logs`: Records hash-chained security event.
    - `GET /api/v1/security/audit-logs`: Queries audit trails with filtering.
    - `GET /api/v1/security/audit-logs/verify`: Cryptographically verifies SHA-256 hash chain integrity.
    - `POST /api/v1/security/secrets` & `GET /api/v1/security/secrets`: Vaults and lists secrets with masked previews.
    - `PATCH /api/v1/security/secrets/{id}/revoke` & `DELETE /api/v1/security/secrets/{id}`: Secret lifecycle and revocation.
    - `GET /api/v1/security/policy` & `PATCH /api/v1/security/policy`: Workspace security policy and retention rules.
    - `POST /api/v1/security/gdpr/purge`: GDPR Right-to-be-Forgotten cascade data purge.
    - `GET /api/v1/security/compliance/status`: Real-time SOC 2 Type II and GDPR compliance scorecard.
  - Created interactive Enterprise Security Studio in `apps/web/src/pages/EnterpriseSecurityPage.tsx` with Compliance Scorecard, KMS Secret Vault manager, Tamper-Evident Audit Log explorer, and Retention & GDPR purge controls.
  - Mounted `/security` route in `App.tsx` and added `Enterprise Security` navigation link in `Layout.tsx`.
  - Added test suites in `packages/shared/tests/test_kms_encryption.py`, `packages/database/tests/test_security_repo.py`, and `apps/api/tests/test_security_api.py`, achieving 100% pass rate (309/309 tests passing across monorepo).
  - Formalized **ADR 023** (Enterprise KMS Envelope Encryption, Cryptographic Audit Chains, and GDPR Data Lifecycle Controls).

---

## [1.6.0] - 2026-09-13 (Generation 5 Milestone 3: Phase 22 - Agent Evaluation Engine & Observability Platform)

### Added
- **Phase 22: Agent Evaluation & Observability Platform**:
  - Implemented multi-metric autonomous agent evaluation engine in `packages/ai/src/ai/eval/agent_evaluator.py` (`AgentEvaluator`, `AgentEvaluationScorecard`, `AgentStepTelemetry`, `AgentEvaluationMetric`).
  - Added deterministic scoring functions: Plan Precision (`evaluate_plan_precision`), Tool Accuracy (`evaluate_tool_accuracy`), Evidence Coverage (`evaluate_evidence_coverage`), and sentence-level Hallucination Rate (`evaluate_hallucination_rate`).
  - Implemented database models `DBAgentEvaluation` and `DBAgentStepMetric` in `packages/database/src/database/models/agent_evaluation.py` with full PostgreSQL/SQLite parity.
  - Implemented `AgentEvaluationRepository` in `packages/database/src/database/repositories/agent_evaluation_repo.py` supporting evaluation scorecard persistence, step telemetry inspection, and aggregate KPI calculation.
  - Implemented REST API endpoints in `apps/api/src/api/routes/agent_evaluations.py`:
    - `POST /api/v1/agents/evaluate`: Evaluates an agent execution run or research job.
    - `GET /api/v1/agents/evaluations`: Lists historical evaluations with agent and job filters.
    - `GET /api/v1/agents/evaluations/{id}`: Retrieves detailed evaluation scorecard and sequential step telemetry.
    - `DELETE /api/v1/agents/evaluations/{id}`: Deletes evaluation run.
    - `GET /api/v1/agents/metrics/summary`: Returns system-wide quality, evidence coverage, hallucination rate, token usage, and cost aggregates.
  - Created interactive Agent Observability Studio in `apps/web/src/pages/AgentEvaluationPage.tsx` with KPI scorecards, per-agent architecture badges, historical evaluation runs table, run audit modal, and sequential step telemetry inspector drawer.
  - Integrated `/agents/evaluations` route into `App.tsx` and added `Agent Observability` navigation link to `Layout.tsx`.
  - Added comprehensive test suites in `packages/ai/tests/test_agent_evaluator.py`, `packages/database/tests/test_agent_evaluation_repo.py`, and `apps/api/tests/test_agent_evaluation_api.py`, achieving 100% pass rate (299/299 tests passing).
  - Formalized **ADR 022** (Autonomous Agent Evaluation and Hallucination Observability Engine).

---

## [1.5.0] - 2026-09-13 (Generation 5 Milestone 2: Phase 21 - Model Evaluation System)

### Added
- **Phase 21: Model Evaluation System**:
  - Implemented standardized golden benchmark suite in `packages/ai/src/ai/eval/schemas.py` (`BenchmarkCategory`, `BenchmarkSample`, `BenchmarkDataset`, and `DEFAULT_RESEARCH_BENCHMARK`).
  - Implemented `EvaluationMetricsEngine` in `packages/ai/src/ai/eval/metrics.py` computing quantitative scores across Factual Accuracy, Reasoning Depth, Retrieval Faithfulness, Citation Precision, Latency, and Cost.
  - Implemented `ModelEvaluator` in `packages/ai/src/ai/eval/evaluator.py` orchestrating end-to-end evaluation runs with low temperature against `ModelGateway`.
  - Implemented database models `DBModelEvaluation` and `DBModelBenchmarkResult` in `packages/database/src/database/models/evaluation.py` with full PostgreSQL/SQLite parity.
  - Implemented `ModelEvaluationRepository` in `packages/database/src/database/repositories/evaluation_repo.py` supporting evaluation CRUD, latest-per-model queries, and test case relationship queries.
  - Created REST API endpoints in `apps/api/src/api/routes/evaluation.py`:
    - `POST /api/v1/models/evaluate`: Triggers evaluation runs.
    - `GET /api/v1/models/evaluations`: Lists historical evaluation runs.
    - `GET /api/v1/models/evaluations/{id}`: Retrieves detailed sample test case breakdown.
    - `DELETE /api/v1/models/evaluations/{id}`: Deletes evaluation run.
    - `GET /api/v1/models/leaderboard`: Returns aggregated competitive leaderboard with Pareto optimal badges.
  - Created interactive React Leaderboard Studio `ModelEvaluationPage.tsx` with ranking table, benchmark runner modal, score progress bars, and test case breakdown drawer.
  - Added unit, database repository, and integration test suites in `packages/ai/tests/test_model_evaluator.py`, `packages/database/tests/test_evaluation_repo.py`, and `apps/api/tests/test_model_evaluation_api.py`, achieving 100% pass rate across 291 monorepo tests.
  - Formalized **ADR 021** (Automated Model Evaluation System with Golden Benchmark Harness and Competitive Leaderboard).

---

## [1.4.0] - 2026-09-13 (Generation 5 Milestone 1: Phase 20 - Intelligent Model Ecosystem)

### Added
- **Phase 20: Intelligent Model Ecosystem**:
  - Implemented `ModelEcosystemOptimizer` in `packages/ai/src/ai/router/optimizer.py` with multi-parameter utility scoring formula: $\text{Score}(M) = w_q \cdot Q(M) + w_s \cdot S(M) + w_c \cdot C(M) + w_l \cdot L(M)$.
  - Implemented non-dominated Pareto-frontier sorting across Quality, Speed, and Cost Efficiency dimensions.
  - Defined preset `OptimizationProfile` schemas (`Balanced`, `Cost Minimized`, `Speed Maximized`, `Quality & Reasoning Maximized`, `Custom`).
  - Integrated routing profile awareness into `ModelRouter` (`packages/ai/src/ai/providers/router.py`) and `ModelGateway` (`packages/ai/src/ai/gateway/model_gateway.py`), attaching `routing_profile` to execution telemetry.
  - Implemented REST API endpoints in `apps/api/src/api/routes/models.py`:
    - `GET /api/v1/models/profiles`: Returns preset optimization profiles with normalized weight breakdowns.
    - `POST /api/v1/models/optimize`: Simulates candidate model ranking, Pareto-frontier identification, and itemized trade-off rationale.
  - Upgraded `NewResearch.tsx` with interactive profile selector cards and live simulation preview.
  - Formalized **ADR 020** (Intelligent Model Ecosystem with Multi-Parameter Routing Optimization and Pareto-Frontier Selection).
  - Added unit and integration test suites in `packages/ai/tests/test_model_ecosystem_optimizer.py` and `apps/api/tests/test_model_optimization_api.py`, achieving 100% pass rate across 283 monorepo tests.

---

## [1.3.0] - 2026-09-13 (Generation 4 Milestone 2: Phase 19 - Team Collaboration)

### Added
- **Phase 19: Team Collaboration**:
  - Implemented `DBWorkspaceInvite`, `DBReportAnnotation`, and `DBWorkspaceActivity` database models in `packages/database/src/database/models/collaboration.py` with URL-safe crypto token generation, 7-day expiration, and dialect-safe `GUID`/`JSONType`.
  - Implemented `WorkspaceInviteRepository`, `ReportAnnotationRepository`, and `WorkspaceActivityRepository` in `packages/database/src/database/repositories/collaboration_repo.py` supporting token redemption, multi-role membership upgrade, threaded report annotations with quotes and resolution tracking, and chronological activity auditing.
  - Created REST API endpoints in `apps/api/src/api/routes/collaboration.py`:
    - `/api/v1/workspaces/{id}/invites` (POST, GET)
    - `/api/v1/invites/{token}` (GET)
    - `/api/v1/invites/{token}/accept` (POST)
    - `/api/v1/invites/{id}` (DELETE)
    - `/api/v1/reports/{id}/annotations` (POST, GET)
    - `/api/v1/annotations/{id}/resolve` (PATCH)
    - `/api/v1/annotations/{id}` (DELETE)
    - `/api/v1/workspaces/{id}/activities` (GET)
    - `/api/v1/projects/{id}/activities` (GET)
  - Built React collaboration components:
    - `WorkspaceMembersModal.tsx`: Real-time member roster, role badges, email invitation modal, invite link copy button, and pending invite revocation.
    - `ReportAnnotationsDrawer.tsx`: Slide-over review drawer on `ResearchDetail.tsx` with section quotes, comment threads, filter tabs (All, Open, Resolved), and 1-click resolution.
    - Integrated team access modal into `ProjectsPage.tsx` and review notes trigger into `ResearchDetail.tsx`.
  - Formalized **ADR 019** (Team Collaboration, Workspace Invites, Report Annotations, and Activity Feed).
  - Added unit and integration test suites in `packages/database/tests/test_collaboration_repo.py` and `apps/api/tests/test_collaboration_api.py`, achieving 100% pass rate across all 276 monorepo tests.

---

## [1.2.0] - 2026-09-13 (Generation 4 Milestone 1: Phase 18)

### Added
- **Phase 18: Projects & Workspaces**:
  - Implemented `DBWorkspace`, `DBWorkspaceMember`, and `DBProject` database models in `packages/database/src/database/models/workspace.py` with cross-database dialect-safe `GUID`, `JSONType`, multi-role membership (`owner`, `admin`, `researcher`, `member`, `viewer`), and collision-resistant slug generation.
  - Extended existing models (`ResearchJob`, `Document`, `DBResearchMemory`, `DBKnowledgeEntity`) with `workspace_id` and `project_id` foreign keys and compound indexes for full tenant isolation.
  - Implemented `WorkspaceRepository` and `ProjectRepository` in `packages/database/src/database/repositories/` with auto-provisioning of personal workspaces and default projects, membership RBAC queries, and aggregate statistical overview queries (`total_jobs`, `total_documents`, `total_memories`, `total_graph_entities`).
  - Created complete FastAPI REST API endpoints in `apps/api/src/api/routes/workspaces.py` and `apps/api/src/api/routes/projects.py` with dependency injection in `dependencies.py` and registration in `main.py`.
  - Upgraded `ResearchPipeline` and `IngestionPipeline` to accept, propagate, and filter by `workspace_id` and `project_id`.
  - Built `WorkspaceContext.tsx` global provider, `WorkspaceSelector.tsx` dropdown in sidebar navigation, and dedicated `ProjectsPage.tsx` management dashboard in `apps/web`.
  - Formalized **ADR 018** (Multi-Tenant Workspace & Project Hierarchy).
  - Added unit and integration test suites in `packages/database/tests/test_workspace_project_repo.py` and `apps/api/tests/test_workspaces_projects_api.py`, achieving 100% pass rate across all 270 monorepo tests.

---

## [1.1.0] - 2026-09-12 (Branch: `develop/v1.1`)

### Added
- **Phase 17: Long-Term Knowledge Graph**:
  - Implemented `DBKnowledgeEntity` and `DBKnowledgeRelation` database models in `packages/database/src/database/models/graph.py` with cross-database dialect-safe `GUID`, `JSONType`, entity categories (`concept`, `person`, `organization`, `technology`, `methodology`, `finding`, `dataset`, `metric`, `other`), aliases, and properties.
  - Implemented `KnowledgeGraphRepository` in `packages/database/src/database/repositories/graph_repo.py` supporting CRUD, entity name canonicalization, batch triplet upserting, $k$-hop BFS neighborhood extraction (`get_k_hop_subgraph`), and shortest-path multi-hop traversal (`find_shortest_path`).
  - Implemented `KnowledgeGraphEngine` in `packages/research/src/research/graph/engine.py` orchestrating automated triplet extraction from research findings, LLM fallback parsing, Graph-Augmented RAG (`GraphRAG`), and semantic pathfinding.
  - Added Agent graph tools in `packages/tools/src/tools/definitions/graph.py`: `QueryKnowledgeGraphTool`, `ExtractGraphTripletsTool`, and `FindRelationPathTool` with lazy loading to prevent circular import chains.
  - Created complete FastAPI REST API endpoints in `apps/api/src/api/routes/graph.py` (`/nodes`, `/edges`, `/subgraph`, `/paths`, `/extract`, `/stats`) wired in `dependencies.py` and `main.py`.
  - Added WebSocket real-time events: `GRAPH_ENTITIES_EXTRACTED` and `GRAPH_RELATIONS_EXTRACTED`.
  - Developed interactive React network studio `KnowledgeGraphViewer.tsx` and `KnowledgeGraphPage.tsx` with dynamic SVG force layouts, node dragging, pan/zoom, type color badges, multi-hop pathfinding explorer, and direct integration into `ResearchDetail.tsx` and `Layout.tsx`.
  - Formalized **ADR 017** (Long-Term Knowledge Graph & GraphRAG via In-Database Adjacency vs External Graph DBs).
  - Added unit test suites across all layers (`test_knowledge_graph_repository.py`, `test_knowledge_graph_engine.py`, `test_knowledge_graph_tools.py`, `test_graph_api.py`), achieving 100% pass rate (265/265 tests).
- **Phase 16: Research Memory**:
  - Implemented `DBResearchMemory` database model in `packages/database/src/database/models/memory.py` supporting dialect-safe JSON/GUID types, memory types (`concept`, `finding`, `hypothesis`, `methodology`, `fact`), tagging, confidence scores, provenance, and access statistics (`access_count`, `last_accessed_at`).
  - Implemented `MemoryRepository` in `packages/database/src/database/repositories/memory_repository.py` providing transactional async CRUD, keyword/text search across titles/content/tags, access incrementing, and count aggregations.
  - Implemented `ResearchMemoryManager` in `packages/research/src/research/memory/manager.py` with `recall_memories()`, prompt formatting, and `store_memories_from_report()` for automated post-synthesis persistence of distilled findings, methodologies, and hypotheses.
  - Integrated research memory recall into `PlannerAgent` context in `packages/research/src/research/pipeline.py` and `packages/agents/src/agents/planner/planner_agent.py`.
  - Added `RecallMemoryTool` and `StoreMemoryTool` in `packages/tools/src/tools/definitions/memory.py` allowing autonomous agents to query and persist memory items during research execution.
  - Created FastAPI REST endpoints in `apps/api/src/api/routes/memory.py` (`GET /`, `POST /`, `GET /search`, `GET /{id}`, `PATCH /{id}`, `DELETE /{id}`) with dependency injection in `apps/api/src/api/dependencies.py`.
  - Added `MEMORY_RECALLED` and `MEMORY_STORED` WebSocket domain events in `ResearchEventType`.
  - Built interactive `ResearchMemoryViewer.tsx` React component with rich dark theme, type filtering, confidence gauges, tag filtering, access stats, and manual creation modals.
  - Added dedicated `/memory` route in `apps/web/src/App.tsx`, nav link in `apps/web/src/components/Layout.tsx`, and a Memories tab in `apps/web/src/pages/ResearchDetail.tsx`.
  - Added unit test suites in `packages/database/tests/test_memory_repository.py`, `packages/research/tests/test_research_memory.py`, `packages/tools/tests/test_memory_tools.py`, and `apps/api/tests/test_memory_api.py`, achieving 100% pass rate across all 256 monorepo tests.
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
