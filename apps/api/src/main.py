from api.routes.whole_exome_tmb_msi_ranker import router as whole_exome_tmb_msi_ranker_router
from api.routes.synthetic_riboswitch_aptamer import router as synthetic_riboswitch_aptamer_router
from api.routes.targeted_covalent_inhibitor_warhead import router as targeted_covalent_inhibitor_warhead_router
from api.routes.spatial_transcriptomics_celltype import router as spatial_transcriptomics_celltype_router
from api.routes.cryoem_flexible_backbone_refine import router as cryoem_flexible_backbone_refine_router
from api.routes.immunopeptidome_deconvolution import router as immunopeptidome_deconvolution_router
from api.routes.cpg_island_hypermethylation import router as cpg_island_hypermethylation_router
from api.routes.scrna_copy_number_karyotype import router as scrna_copy_number_karyotype_router
from api.routes.optogenetics_photostimulation import router as optogenetics_photostimulation_router
from api.routes.milestone_v2_3_orchestrator import router as milestone_v2_3_orchestrator_router
from api.routes.long_read_sv_assembly import router as long_read_sv_assembly_router
from api.routes.ubiquitination_e3_selectivity import router as ubiquitination_e3_selectivity_router
from api.routes.multiome_atac_gex_cisreg import router as multiome_atac_gex_cisreg_router
from api.routes.synthetic_gene_toggle_switch import router as synthetic_gene_toggle_switch_router
from api.routes.fep_binding_affinity import router as fep_binding_affinity_router
from api.routes.spatial_tme_immune_infiltration import router as spatial_tme_immune_infiltration_router
from api.routes.scrnaseq_ambient_scrubber import router as scrnaseq_ambient_scrubber_router
from api.routes.mrna_lnp_encapsulation import router as mrna_lnp_encapsulation_router
from api.routes.hichip_chromatin_looping import router as hichip_chromatin_looping_router
from api.routes.spatial_lipidomics_profiling import router as spatial_lipidomics_profiling_router
from api.routes.car_nk_cytolytic_synapse import router as car_nk_cytolytic_synapse_router
from api.routes.cryoem_focused_refinement import router as cryoem_focused_refinement_router
from api.routes.riboseq_translation_kinetics import router as riboseq_translation_kinetics_router
from api.routes.crispr_cas13_rna_targeting import router as crispr_cas13_rna_targeting_router
from api.routes.ctdna_liquid_biopsy_mrd import router as ctdna_liquid_biopsy_mrd_router
from api.routes.aso_gapmer_therapeutics import router as aso_gapmer_therapeutics_router
from api.routes.cryoem_manifold_dynamics import router as cryoem_manifold_dynamics_router
from api.routes.cellular_barcoding_lineage import router as cellular_barcoding_lineage_router
from api.routes.thermal_proteome_profiling import router as thermal_proteome_profiling_router
from api.routes.nanopore_direct_rna import router as nanopore_direct_rna_router
from api.routes.spatial_maldi_metabolomics import router as spatial_maldi_metabolomics_router
from api.routes.milestone_v2_1_orchestrator import router as milestone_v2_1_orchestrator_router
from api.routes.radiomics_deep_phenotyping import router as radiomics_deep_phenotyping_router
from api.routes.neoantigen_hla_presentation import router as neoantigen_hla_presentation_router
from api.routes.fragment_based_lead_discovery import router as fragment_based_lead_discovery_router
from api.routes.car_t_exhaustion_kinetics import router as car_t_exhaustion_kinetics_router
from api.routes.microbiome_metabolomics_axis import router as microbiome_metabolomics_axis_router
from api.routes.rare_disease_hpo_phenotyping import router as rare_disease_hpo_phenotyping_router
from api.routes.crispr_prime_editing_pegdna import router as crispr_prime_editing_pegdna_router
from api.routes.circrna_biogenesis import router as circrna_biogenesis_router
from api.routes.adc_dar_optimization import router as adc_dar_optimization_router
from api.routes import milestone_v1_9
from api.routes import smfret_kinetics
from api.routes import crispr_epigenetic
from api.routes import tcell_engager
from api.routes import cfps_txtl
from api.routes import protac_kinetics
from api.routes import spatial_proteomics_codex
from api.routes import milestone_v1_8
from api.routes import mrna_codon
from api.routes import chromatin_loop
from api.routes import capsid_assembly
from api.routes import spatial_flux
from api.routes import dna_origami
from api.routes import glycan_microarray
from api.routes import organoid_morphometry
from api.routes.cryoet_subtomogram_tomography import router as cryoet_subtomogram_tomography_router
from api.routes.hdx_ms_epitope_mapping import router as hdx_ms_epitope_mapping_router
from api.routes.metabolic_flux_fba import router as metabolic_flux_fba_router
from api.routes.spatial_proteogenomics import router as spatial_proteogenomics_router
from api.routes.alphafold_complex_docking import router as alphafold_complex_docking_router
from api.routes.sirna_thermodynamics import router as sirna_thermodynamics_router
from api.routes.cadd_variant_pathogenicity import router as cadd_variant_pathogenicity_router
from api.routes.dna_methylation_clock import router as dna_methylation_clock_router
from api.routes.tcr_clonotype_tracking import router as tcr_clonotype_tracking_router
from api.routes.whole_body_pbpk import router as whole_body_pbpk_router
from api.routes.single_cell_perturbation import router as single_cell_perturbation_router
from api.routes.microed_structural import router as microed_structural_router
from api.routes.pdc_conjugate import router as pdc_conjugate_router
from api.routes.crispr_base_editor import router as crispr_base_editor_router
from api.routes.rna_thermodynamics import router as rna_thermodynamics_router
from api.routes.spatial_microdissection import router as spatial_microdissection_router
from api.routes.spatial_rna_velocity import router as spatial_rna_velocity_router
from api.routes.tcr_pmhc import router as tcr_pmhc_router
from api.routes.mitochondrial_bioenergetics import router as mitochondrial_bioenergetics_router
from api.routes.aptamer_evolution import router as aptamer_evolution_router
from api.routes.cyp450_metabolism import router as cyp450_metabolism_router
from api.routes.clinical_epro import router as clinical_epro_router
from api.routes.membrane_permeability import router as membrane_permeability_router
from api.routes.spatial_gnn_neighborhood import router as spatial_gnn_router
from api.routes.lnp_encapsulation import router as lnp_encapsulation_router
from api.routes.car_macrophage import router as car_macrophage_router
from api.routes.histone_acetylation import router as histone_acetylation_router
from api.routes.hla_loh_resistance import router as hla_loh_router
from api.routes.riboswitch_kinetics import router as riboswitch_kinetics_router
from api.routes.cryoet_clustering import router as cryoet_clustering_router
from api.routes.viral_phylodynamics import router as viral_phylodynamics_router
from api.routes.biocomputer_logic import router as biocomputer_logic_router
from api.routes.adaptive_resistance import router as adaptive_resistance_router
from api.routes.pandda_crystallography import router as pandda_crystallography_router
from api.routes.citeseq import router as citeseq_router
from api.routes.antibody_maturation import router as antibody_maturation_router
from api.routes.t2t_assembly import router as t2t_assembly_router
from api.routes.milestone_v1_6 import router as milestone_v1_6_router
from api.routes.preprint_latex import router as preprint_latex_router
from api.routes.bgc_mining import router as bgc_router
from api.routes.trial_telemetry import router as trial_telemetry_router
from api.routes.tpd_molecular_glue import router as tpd_router
from api.routes.multiome_joint import router as multiome_router
from api.routes.ddr_pathways import router as ddr_router
from api.routes.pmhc_class2 import router as pmhc_class2_router
from api.routes.cryo_dynamic_manifold import router as cryo_manifold_router
from api.routes.spatial_metabolite_imaging import router as spatial_msi_router
from api.routes.mirna_regulation import router as mirna_router
from api.routes.lineage_tracing import router as lineage_router
from api.routes.tce_bispecific import router as tce_router
from api.routes.histone_epigenetics import router as histone_epigenetics_router
from api.routes.ctc_metastasis import router as ctc_router
from api.routes.survival_prognosis import router as survival_prognosis_router
from api.routes.cytof import router as cytof_router
from api.routes.organ_chip import router as organ_chip_router
from api.routes.cryptic_pockets import router as cryptic_pockets_router
from api.routes.spatial_lipidomics import router as spatial_lipidomics_router
from api.routes.hdx_ms import router as hdx_ms_router
from api.routes.immune_repertoire import router as immune_repertoire_router
from api.routes.literature_factcheck import router as factcheck_router
from api.routes.spatial_proteomics import router as spatial_proteomics_router
from api.routes.prime_editing import router as prime_editing_router
from api.routes.experiment_synthesis import router as experiment_synthesis_router
from api.routes.pkpd_simulation import router as pkpd_router
from api.routes.sirna_design import router as sirna_design_router
from api.routes.cryo_ensemble import router as cryo_ensemble_router
from api.routes.car_nk import router as car_nk_router
from api.routes.proteogenomics import router as proteogenomics_router
from api.routes.spatial_transcriptomics import router as spatial_transcriptomics_router
from api.routes.preclinical_toxicology import router as preclinical_toxicology_router
from api.routes.synthetic_gene_circuit import router as gene_circuit_router
from api.routes.phenotypic_screening import router as phenotypic_screening_router
from api.routes.epigenetic_clock import router as epigenetic_clock_router
from api.routes.robotic_workcell import router as robotic_workcell_router
from api.routes.radiogenomics import router as radiogenomics_router
from api.routes.clinical_genomics_twin import router as clinical_twin_router
from api.routes.whole_cell_metabolism import router as whole_cell_router
from api.routes.diffusion_conformation import router as diffusion_router
from api.routes.long_read_genomics import router as long_read_router
from api.routes.quantum_chemistry import router as quantum_chemistry_router
from api.routes.amr_surveillance import router as amr_surveillance_router
from api.routes.lnp_formulation import router as lnp_formulation_router
from api.routes.biomarker_discovery import router as biomarker_discovery_router
from api.routes.smfret import router as smfret_router
from api.routes.chemogenomics import router as chemogenomics_router
from api.routes.cryoet_subtomogram import router as cryoet_subtomogram_router
from api.routes.pv_signal_mining import router as pv_signal_mining_router
from api.routes.liquid_biopsy import router as liquid_biopsy_router
from api.routes.variant_pathogenicity import router as variant_pathogenicity_router
from api.routes.clinical_site_selection import router as clinical_site_selection_router
from api.routes.gene_circuit_burden import router as circuit_burden_router
from api.routes.toxicity_qsar import router as toxicity_router
from api.routes.synthetic_lethality import router as lethality_router
from api.routes.biotherapeutic_stability import router as stability_router
from api.routes.flow_cytometry import router as flow_cytometry_router
from api.routes.cancer_vaccines import router as cancer_vaccines_router
from api.routes.vhts import router as vhts_router
from api.routes.immunology import router as immunology_router
from api.routes.epigenomics import router as epigenomics_router
from api.routes.spatial_metabolomics import router as spatial_metabolomics_router
from api.routes.ppi_interactome import router as ppi_interactome_router
from api.routes.adc_design import router as adc_design_router
from api.routes.pbpk_nanomedicine import router as pbpk_nanomedicine_router
from api.routes.rare_disease_hpo import router as rare_disease_hpo_router
from api.routes.bioprocess_digital_twin import router as bioprocess_router
from api.routes.clinical_logistics import router as clinical_logistics_router
from api.routes.peer_review import router as peer_review_router
from api.routes.synthetic_biology import router as synbio_router
from api.routes.cart_engineering import router as cart_router
from api.routes.eln import router as eln_router
from api.routes.lakehouse import router as lakehouse_router
from api.routes.ragas_eval import router as ragas_eval_router
from api.routes.ai_scientist import router as ai_scientist_router
from api.routes.pharmacovigilance import router as pv_router
from api.routes.pathway_perturbation import router as pathways_router
from api.routes.cryoem import router as cryoem_router
from api.routes.clinical_trials import router as clinical_trials_router
from api.routes.drug_synergy import router as synergy_router
from api.routes.super_graph import router as supergraph_router
from api.routes.generative_chemistry import router as chemistry_router
from api.routes.spatial import router as spatial_router
"""FastAPI application entry point."""

from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from shared.config import settings
from shared.logging import setup_logging, get_logger
from shared.exceptions import ResearchError
from database.connection import init_db, close_db
from api.routes import clinical_trials
from api.routes import agent_evaluations, auth, automation, canvas, clinical, collaboration, crispr, dataset_synthesis, debate, developer, documents, evaluation, grant_proposals, graph, health, lab_automation, literature, memory, metrics, models, molecular, molecular_dynamics, patents, peer_review, presentations, projects, reproducibility, research, security, single_cell, system_infra, workspaces
from api import websocket



from api.middleware.metrics import PrometheusMiddleware

logger = get_logger(__name__)

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    logger.info("Starting application", version=settings.app_version)
    await init_db()
    
    # Initialize model providers
    from api.dependencies import init_providers
    await init_providers()
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    await close_db()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Prometheus metrics middleware
app.add_middleware(PrometheusMiddleware)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(ResearchError)
async def research_error_handler(request: Request, exc: ResearchError):
    logger.error("Research error", path=request.url.path, error=exc.to_dict())
    return JSONResponse(status_code=400, content=exc.to_dict())

@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error", path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "Internal server error"}},
    )

from uuid import uuid4

# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    request.state.request_id = request_id
    
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# Include routers
app.include_router(cryoet_subtomogram_tomography_router, prefix="/api/v1")
app.include_router(hdx_ms_epitope_mapping_router, prefix="/api/v1")
app.include_router(metabolic_flux_fba_router, prefix="/api/v1")
app.include_router(spatial_proteogenomics_router, prefix="/api/v1")
app.include_router(alphafold_complex_docking_router, prefix="/api/v1")
app.include_router(sirna_thermodynamics_router, prefix="/api/v1")
app.include_router(cadd_variant_pathogenicity_router, prefix="/api/v1")
app.include_router(dna_methylation_clock_router, prefix="/api/v1")
app.include_router(tcr_clonotype_tracking_router, prefix="/api/v1")
app.include_router(whole_body_pbpk_router, prefix="/api/v1")
app.include_router(single_cell_perturbation_router, prefix="/api/v1")
app.include_router(microed_structural_router, prefix="/api/v1")
app.include_router(pdc_conjugate_router, prefix="/api/v1")
app.include_router(crispr_base_editor_router, prefix="/api/v1")
app.include_router(rna_thermodynamics_router, prefix="/api/v1")
app.include_router(spatial_microdissection_router, prefix="/api/v1")
app.include_router(spatial_gnn_router, prefix="/api/v1")
app.include_router(lnp_encapsulation_router, prefix="/api/v1")
app.include_router(car_macrophage_router, prefix="/api/v1")
app.include_router(histone_acetylation_router, prefix="/api/v1")
app.include_router(hla_loh_router, prefix="/api/v1")
app.include_router(riboswitch_kinetics_router, prefix="/api/v1")
app.include_router(cryoet_clustering_router, prefix="/api/v1")
app.include_router(viral_phylodynamics_router, prefix="/api/v1")
app.include_router(biocomputer_logic_router, prefix="/api/v1")
app.include_router(adaptive_resistance_router, prefix="/api/v1")
app.include_router(pandda_crystallography_router, prefix="/api/v1")
app.include_router(citeseq_router, prefix="/api/v1")
app.include_router(antibody_maturation_router, prefix="/api/v1")
app.include_router(t2t_assembly_router, prefix="/api/v1")
app.include_router(membrane_permeability_router, prefix="/api/v1")
app.include_router(clinical_epro_router, prefix="/api/v1")
app.include_router(cyp450_metabolism_router, prefix="/api/v1")
app.include_router(aptamer_evolution_router, prefix="/api/v1")
app.include_router(mitochondrial_bioenergetics_router, prefix="/api/v1")
app.include_router(tcr_pmhc_router, prefix="/api/v1")
app.include_router(spatial_rna_velocity_router, prefix="/api/v1")
app.include_router(milestone_v1_6_router, prefix="/api/v1")
app.include_router(preprint_latex_router, prefix="/api/v1")
app.include_router(bgc_router, prefix="/api/v1")
app.include_router(trial_telemetry_router, prefix="/api/v1")
app.include_router(tpd_router, prefix="/api/v1")
app.include_router(multiome_router, prefix="/api/v1")
app.include_router(ddr_router, prefix="/api/v1")
app.include_router(pmhc_class2_router, prefix="/api/v1")
app.include_router(cryo_manifold_router, prefix="/api/v1")
app.include_router(spatial_msi_router, prefix="/api/v1")
app.include_router(mirna_router, prefix="/api/v1")
app.include_router(lineage_router, prefix="/api/v1")
app.include_router(tce_router, prefix="/api/v1")
app.include_router(histone_epigenetics_router, prefix="/api/v1")
app.include_router(ctc_router, prefix="/api/v1")
app.include_router(survival_prognosis_router, prefix="/api/v1")
app.include_router(cytof_router, prefix="/api/v1")
app.include_router(organ_chip_router, prefix="/api/v1")
app.include_router(cryptic_pockets_router, prefix="/api/v1")
app.include_router(spatial_lipidomics_router, prefix="/api/v1")
app.include_router(hdx_ms_router, prefix="/api/v1")
app.include_router(immune_repertoire_router, prefix="/api/v1")
app.include_router(factcheck_router, prefix="/api/v1")
app.include_router(spatial_proteomics_router, prefix="/api/v1")
app.include_router(prime_editing_router, prefix="/api/v1")
app.include_router(experiment_synthesis_router, prefix="/api/v1")
app.include_router(pkpd_router, prefix="/api/v1")
app.include_router(sirna_design_router, prefix="/api/v1")
app.include_router(cryo_ensemble_router, prefix="/api/v1")
app.include_router(car_nk_router, prefix="/api/v1")
app.include_router(proteogenomics_router, prefix="/api/v1")
app.include_router(spatial_transcriptomics_router, prefix="/api/v1")
app.include_router(preclinical_toxicology_router, prefix="/api/v1")
app.include_router(gene_circuit_router, prefix="/api/v1")
app.include_router(phenotypic_screening_router, prefix="/api/v1")
app.include_router(epigenetic_clock_router, prefix="/api/v1")
app.include_router(robotic_workcell_router, prefix="/api/v1")
app.include_router(radiogenomics_router, prefix="/api/v1")
app.include_router(clinical_twin_router, prefix="/api/v1")
app.include_router(whole_cell_router, prefix="/api/v1")
app.include_router(diffusion_router, prefix="/api/v1")
app.include_router(long_read_router, prefix="/api/v1")
app.include_router(quantum_chemistry_router, prefix="/api/v1")
app.include_router(amr_surveillance_router)
app.include_router(lnp_formulation_router)
app.include_router(biomarker_discovery_router)
app.include_router(smfret_router)
app.include_router(chemogenomics_router)
app.include_router(cryoet_subtomogram_router)
app.include_router(pv_signal_mining_router)
app.include_router(liquid_biopsy_router)
app.include_router(variant_pathogenicity_router)
app.include_router(clinical_site_selection_router)
app.include_router(circuit_burden_router)
app.include_router(toxicity_router)
app.include_router(lethality_router)
app.include_router(stability_router)
app.include_router(flow_cytometry_router)
app.include_router(cancer_vaccines_router)
app.include_router(vhts_router, prefix="/api/v1")
app.include_router(immunology_router, prefix="/api/v1")
app.include_router(epigenomics_router, prefix="/api/v1")
app.include_router(spatial_metabolomics_router, prefix="/api/v1")
app.include_router(ppi_interactome_router, prefix="/api/v1")
app.include_router(adc_design_router, prefix="/api/v1")
app.include_router(pbpk_nanomedicine_router, prefix="/api/v1")
app.include_router(rare_disease_hpo_router, prefix="/api/v1")
app.include_router(bioprocess_router, prefix="/api/v1")
app.include_router(clinical_logistics_router, prefix="/api/v1")
app.include_router(peer_review_router, prefix="/api/v1")
app.include_router(synbio_router, prefix="/api/v1")
app.include_router(cart_router, prefix="/api/v1")
app.include_router(eln_router, prefix="/api/v1")
app.include_router(lakehouse_router, prefix="/api/v1")
app.include_router(ragas_eval_router, prefix="/api/v1")
app.include_router(ai_scientist_router, prefix="/api/v1")
app.include_router(pv_router, prefix="/api/v1")
app.include_router(pathways_router, prefix="/api/v1")
app.include_router(cryoem_router, prefix="/api/v1")
app.include_router(clinical_trials_router, prefix="/api/v1")
app.include_router(synergy_router, prefix="/api/v1")
app.include_router(supergraph_router, prefix="/api/v1")
app.include_router(chemistry_router, prefix="/api/v1")
app.include_router(spatial_router, prefix="/api/v1")
app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(research.router, prefix=settings.api_prefix)
app.include_router(websocket.router, prefix=settings.api_prefix)
app.include_router(documents.router, prefix=settings.api_prefix)
app.include_router(workspaces.router, prefix=settings.api_prefix)
app.include_router(projects.router, prefix=settings.api_prefix)
app.include_router(collaboration.router, prefix=settings.api_prefix)
app.include_router(memory.router, prefix=settings.api_prefix)
app.include_router(graph.router, prefix=settings.api_prefix)
app.include_router(models.router, prefix=settings.api_prefix)
app.include_router(evaluation.router, prefix=settings.api_prefix)
app.include_router(agent_evaluations.router, prefix=settings.api_prefix)
app.include_router(security.router, prefix=settings.api_prefix)
app.include_router(system_infra.router, prefix=settings.api_prefix)
app.include_router(developer.router, prefix=settings.api_prefix)
app.include_router(automation.router, prefix=settings.api_prefix)
app.include_router(debate.router, prefix=settings.api_prefix)
app.include_router(literature.router, prefix=settings.api_prefix)
app.include_router(reproducibility.router, prefix=settings.api_prefix)
app.include_router(presentations.router, prefix=settings.api_prefix)
app.include_router(peer_review.router, prefix=settings.api_prefix)
app.include_router(canvas.router, prefix=settings.api_prefix)
app.include_router(dataset_synthesis.router, prefix=settings.api_prefix)
app.include_router(patents.router, prefix=settings.api_prefix)
app.include_router(grant_proposals.router, prefix=settings.api_prefix)
app.include_router(clinical.router, prefix=settings.api_prefix)
app.include_router(lab_automation.router, prefix=settings.api_prefix)
app.include_router(molecular.router, prefix=settings.api_prefix)
app.include_router(molecular_dynamics.router, prefix=settings.api_prefix)
app.include_router(crispr.router, prefix=settings.api_prefix)
app.include_router(single_cell.router, prefix=settings.api_prefix)
app.include_router(metrics.router, prefix=settings.api_prefix)
app.include_router(metrics.router)  # Also expose directly on /metrics





@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }



app.include_router(organoid_morphometry.router, prefix=settings.api_prefix)

app.include_router(glycan_microarray.router, prefix=settings.api_prefix)

app.include_router(dna_origami.router, prefix=settings.api_prefix)

app.include_router(spatial_flux.router, prefix=settings.api_prefix)

app.include_router(capsid_assembly.router, prefix=settings.api_prefix)

app.include_router(chromatin_loop.router, prefix=settings.api_prefix)

app.include_router(mrna_codon.router, prefix=settings.api_prefix)

app.include_router(milestone_v1_8.router, prefix=settings.api_prefix)

app.include_router(spatial_proteomics_codex.router, prefix=settings.api_prefix)

app.include_router(protac_kinetics.router, prefix=settings.api_prefix)

app.include_router(cfps_txtl.router, prefix=settings.api_prefix)

app.include_router(tcell_engager.router, prefix=settings.api_prefix)

app.include_router(crispr_epigenetic.router, prefix=settings.api_prefix)

app.include_router(smfret_kinetics.router, prefix=settings.api_prefix)

app.include_router(milestone_v1_9.router, prefix=settings.api_prefix)

app.include_router(adc_dar_optimization_router, prefix=settings.api_prefix)


app.include_router(circrna_biogenesis_router, prefix=settings.api_prefix)


app.include_router(crispr_prime_editing_pegdna_router, prefix=settings.api_prefix)


app.include_router(rare_disease_hpo_phenotyping_router, prefix=settings.api_prefix)


app.include_router(microbiome_metabolomics_axis_router, prefix=settings.api_prefix)


app.include_router(car_t_exhaustion_kinetics_router, prefix=settings.api_prefix)


app.include_router(fragment_based_lead_discovery_router, prefix=settings.api_prefix)


app.include_router(neoantigen_hla_presentation_router, prefix=settings.api_prefix)


app.include_router(radiomics_deep_phenotyping_router, prefix=settings.api_prefix)

app.include_router(milestone_v2_1_orchestrator_router, prefix=settings.api_prefix)

app.include_router(spatial_maldi_metabolomics_router, prefix=settings.api_prefix)

app.include_router(nanopore_direct_rna_router, prefix=settings.api_prefix)

app.include_router(thermal_proteome_profiling_router, prefix=settings.api_prefix)

app.include_router(cellular_barcoding_lineage_router, prefix=settings.api_prefix)

app.include_router(cryoem_manifold_dynamics_router, prefix=settings.api_prefix)

app.include_router(aso_gapmer_therapeutics_router, prefix=settings.api_prefix)

app.include_router(ctdna_liquid_biopsy_mrd_router, prefix=settings.api_prefix)

app.include_router(crispr_cas13_rna_targeting_router, prefix=settings.api_prefix)

app.include_router(riboseq_translation_kinetics_router, prefix=settings.api_prefix)

app.include_router(cryoem_focused_refinement_router, prefix=settings.api_prefix)

app.include_router(car_nk_cytolytic_synapse_router, prefix=settings.api_prefix)

app.include_router(spatial_lipidomics_profiling_router, prefix=settings.api_prefix)

app.include_router(hichip_chromatin_looping_router, prefix=settings.api_prefix)

app.include_router(mrna_lnp_encapsulation_router, prefix=settings.api_prefix)

app.include_router(scrnaseq_ambient_scrubber_router, prefix=settings.api_prefix)

app.include_router(spatial_tme_immune_infiltration_router, prefix=settings.api_prefix)

app.include_router(fep_binding_affinity_router, prefix=settings.api_prefix)

app.include_router(synthetic_gene_toggle_switch_router, prefix=settings.api_prefix)

app.include_router(multiome_atac_gex_cisreg_router, prefix=settings.api_prefix)

app.include_router(ubiquitination_e3_selectivity_router, prefix=settings.api_prefix)

app.include_router(long_read_sv_assembly_router, prefix=settings.api_prefix)

app.include_router(milestone_v2_3_orchestrator_router, prefix=settings.api_prefix)

app.include_router(optogenetics_photostimulation_router, prefix=settings.api_prefix)

app.include_router(scrna_copy_number_karyotype_router, prefix=settings.api_prefix)

app.include_router(cpg_island_hypermethylation_router, prefix=settings.api_prefix)

app.include_router(immunopeptidome_deconvolution_router, prefix=settings.api_prefix)

app.include_router(cryoem_flexible_backbone_refine_router, prefix=settings.api_prefix)

app.include_router(spatial_transcriptomics_celltype_router, prefix=settings.api_prefix)

app.include_router(targeted_covalent_inhibitor_warhead_router, prefix=settings.api_prefix)

app.include_router(synthetic_riboswitch_aptamer_router, prefix=settings.api_prefix)

app.include_router(whole_exome_tmb_msi_ranker_router, prefix=settings.api_prefix)
