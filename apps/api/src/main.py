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


