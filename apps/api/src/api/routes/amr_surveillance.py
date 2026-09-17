"""REST API endpoints for Metagenomic Pathogen Surveillance & AMR Engine."""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.models import User
from database.repositories.amr_surveillance_repo import AMRSurveillanceRepository
from research.amr.amr_engine import MetagenomicAMREngine

router = APIRouter(prefix="/api/v1/amr", tags=["Metagenomic Pathogen & AMR Surveillance"])
engine = MetagenomicAMREngine()


class PathogenInput(BaseModel):
    taxon_name: str
    ncbi_taxid: int = 0
    relative_abundance_pct: float = 1.0
    read_depth: int = 1000
    pathogenicity_grade: str = "OPPORTUNISTIC"
    is_priority_pathogen: bool = False


class AMRGeneInput(BaseModel):
    gene_symbol: str
    resistance_mechanism: str = "BETA_LACTAMASE"
    drug_class: str = "CARBAPENEMS"
    identity_pct: float = 99.0
    coverage_pct: float = 100.0
    plasmid_mediated: bool = True


class AMRSampleRequest(BaseModel):
    sample_name: str
    sample_type: str = "WASTEWATER"
    collection_location: str = "Municipal Facility A"
    total_reads_sequenced: int = Field(5000000, ge=10000, le=1000000000)
    pathogens: Optional[List[PathogenInput]] = None
    amr_genes: Optional[List[AMRGeneInput]] = None


@router.post("/samples/analyze", status_code=status.HTTP_201_CREATED)
async def analyze_metagenomic_sample(
    req: AMRSampleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Analyzes metagenomic sequence data for high-consequence pathogens and AMR resistome."""
    repo = AMRSurveillanceRepository(db)

    pathogens_dict = [p.model_dump() for p in req.pathogens] if req.pathogens else None
    amr_dict = [a.model_dump() for a in req.amr_genes] if req.amr_genes else None

    eval_res = engine.analyze_sample(req.model_dump(), pathogens_dict, amr_dict)

    sample = await repo.create_sample(
        sample_name=eval_res["sample_name"],
        sample_type=eval_res["sample_type"],
        collection_location=eval_res["collection_location"],
        total_reads_sequenced=eval_res["total_reads_sequenced"],
        pathogen_count=eval_res["pathogen_count"],
        amr_genes_count=eval_res["amr_genes_count"],
        outbreak_risk_level=eval_res["outbreak_risk_level"],
        sample_metadata_json=eval_res["sample_metadata_json"],
    )

    created_pathogens = await repo.add_pathogens(sample.id, eval_res["pathogens"])
    created_amr = await repo.add_amr_genes(sample.id, eval_res["amr_genes"])

    return {
        "id": sample.id,
        "sample_name": sample.sample_name,
        "sample_type": sample.sample_type,
        "collection_location": sample.collection_location,
        "total_reads_sequenced": sample.total_reads_sequenced,
        "outbreak_risk_level": sample.outbreak_risk_level,
        "metadata": sample.sample_metadata_json,
        "pathogens": [
            {
                "id": p.id,
                "taxon_name": p.taxon_name,
                "ncbi_taxid": p.ncbi_taxid,
                "relative_abundance_pct": p.relative_abundance_pct,
                "read_depth": p.read_depth,
                "pathogenicity_grade": p.pathogenicity_grade,
                "is_priority_pathogen": p.is_priority_pathogen,
            }
            for p in created_pathogens
        ],
        "amr_genes": [
            {
                "id": a.id,
                "gene_symbol": a.gene_symbol,
                "resistance_mechanism": a.resistance_mechanism,
                "drug_class": a.drug_class,
                "identity_pct": a.identity_pct,
                "coverage_pct": a.coverage_pct,
                "plasmid_mediated": a.plasmid_mediated,
            }
            for a in created_amr
        ]
    }


@router.get("/samples")
async def list_samples(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists metagenomic surveillance samples."""
    repo = AMRSurveillanceRepository(db)
    samples = await repo.list_samples(limit=limit, offset=offset)
    return [
        {
            "id": s.id,
            "sample_name": s.sample_name,
            "sample_type": s.sample_type,
            "collection_location": s.collection_location,
            "pathogen_count": s.pathogen_count,
            "amr_genes_count": s.amr_genes_count,
            "outbreak_risk_level": s.outbreak_risk_level,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in samples
    ]


@router.get("/samples/{sample_id}")
async def get_sample_details(
    sample_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Gets detailed metagenomic sample with pathogens and AMR resistome."""
    repo = AMRSurveillanceRepository(db)
    sample = await repo.get_sample(sample_id)
    if not sample:
        raise HTTPException(status_code=404, detail="Metagenomic surveillance sample not found")

    pathogens = await repo.get_pathogens_by_sample(sample_id)
    amr_genes = await repo.get_amr_genes_by_sample(sample_id)

    return {
        "id": sample.id,
        "sample_name": sample.sample_name,
        "sample_type": sample.sample_type,
        "collection_location": sample.collection_location,
        "total_reads_sequenced": sample.total_reads_sequenced,
        "outbreak_risk_level": sample.outbreak_risk_level,
        "metadata": sample.sample_metadata_json,
        "pathogens": [
            {
                "id": p.id,
                "taxon_name": p.taxon_name,
                "ncbi_taxid": p.ncbi_taxid,
                "relative_abundance_pct": p.relative_abundance_pct,
                "read_depth": p.read_depth,
                "pathogenicity_grade": p.pathogenicity_grade,
                "is_priority_pathogen": p.is_priority_pathogen,
            }
            for p in pathogens
        ],
        "amr_genes": [
            {
                "id": a.id,
                "gene_symbol": a.gene_symbol,
                "resistance_mechanism": a.resistance_mechanism,
                "drug_class": a.drug_class,
                "identity_pct": a.identity_pct,
                "coverage_pct": a.coverage_pct,
                "plasmid_mediated": a.plasmid_mediated,
            }
            for a in amr_genes
        ]
    }
