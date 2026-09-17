"""REST API endpoints for Liquid Biopsy ctDNA Fragmentomics & MRD Detection."""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.models import User
from database.repositories.liquid_biopsy_repo import LiquidBiopsyRepository
from research.liquid_biopsy.fragmentomics_engine import FragmentomicsMRDEngine

router = APIRouter(prefix="/api/v1/liquid-biopsy", tags=["Liquid Biopsy & ctDNA Fragmentomics"])
engine = FragmentomicsMRDEngine()


class SampleAnalysisRequest(BaseModel):
    patient_id: str
    sample_barcode: str
    cancer_type: str = "Colorectal Cancer"
    sampling_timepoint: str = "POST_SURGERY"
    total_cfdna_ng_ml: float = Field(12.5, ge=0.1)
    short_fragments_100_150bp: int = Field(35000, ge=1)
    long_fragments_160_220bp: int = Field(100000, ge=1)


@router.post("/samples/analyze", status_code=status.HTTP_201_CREATED)
async def analyze_liquid_biopsy_sample(
    req: SampleAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Analyzes cfDNA fragment length metrics, 4-mer motifs, infers tumor fraction, and predicts MRD."""
    repo = LiquidBiopsyRepository(db)

    eval_res = engine.analyze_sample(req.model_dump())

    sample = await repo.create_sample(
        patient_id=eval_res["patient_id"],
        sample_barcode=eval_res["sample_barcode"],
        cancer_type=eval_res["cancer_type"],
        sampling_timepoint=eval_res["sampling_timepoint"],
        total_cfdna_ng_ml=eval_res["total_cfdna_ng_ml"],
        tumor_fraction_pct=eval_res["tumor_fraction_pct"],
        mrd_status=eval_res["mrd_status"],
        fragment_short_ratio=eval_res["fragment_short_ratio"],
        median_fragment_length_bp=eval_res["median_fragment_length_bp"],
        sample_metadata_json=eval_res["sample_metadata_json"],
    )

    created_bins = await repo.add_size_distributions(sample.id, eval_res["size_distributions"])
    created_motifs = await repo.add_end_motifs(sample.id, eval_res["end_motifs"])

    return {
        "id": sample.id,
        "patient_id": sample.patient_id,
        "sample_barcode": sample.sample_barcode,
        "cancer_type": sample.cancer_type,
        "sampling_timepoint": sample.sampling_timepoint,
        "total_cfdna_ng_ml": sample.total_cfdna_ng_ml,
        "tumor_fraction_pct": sample.tumor_fraction_pct,
        "mrd_status": sample.mrd_status,
        "fragment_short_ratio": sample.fragment_short_ratio,
        "median_fragment_length_bp": sample.median_fragment_length_bp,
        "metadata": sample.sample_metadata_json,
        "size_distributions": [
            {
                "bin_start_bp": b.bin_start_bp,
                "bin_end_bp": b.bin_end_bp,
                "fragment_count": b.fragment_count,
                "fragment_frequency_pct": b.fragment_frequency_pct,
            }
            for b in created_bins
        ],
        "end_motifs": [
            {
                "motif_sequence_4mer": m.motif_sequence_4mer,
                "observed_frequency": m.observed_frequency,
                "reference_frequency": m.reference_frequency,
                "motif_diversity_score": m.motif_diversity_score,
            }
            for m in created_motifs
        ]
    }


@router.get("/samples")
async def list_samples(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists analyzed liquid biopsy samples."""
    repo = LiquidBiopsyRepository(db)
    samples = await repo.list_samples(limit=limit, offset=offset)
    return [
        {
            "id": s.id,
            "patient_id": s.patient_id,
            "sample_barcode": s.sample_barcode,
            "cancer_type": s.cancer_type,
            "sampling_timepoint": s.sampling_timepoint,
            "tumor_fraction_pct": s.tumor_fraction_pct,
            "mrd_status": s.mrd_status,
            "fragment_short_ratio": s.fragment_short_ratio,
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
    """Gets detailed liquid biopsy sample analysis with fragment distributions and end-motifs."""
    repo = LiquidBiopsyRepository(db)
    sample = await repo.get_sample(sample_id)
    if not sample:
        raise HTTPException(status_code=404, detail="Liquid biopsy sample not found")

    bins = await repo.get_size_distributions_by_sample(sample_id)
    motifs = await repo.get_end_motifs_by_sample(sample_id)

    return {
        "id": sample.id,
        "patient_id": sample.patient_id,
        "sample_barcode": sample.sample_barcode,
        "cancer_type": sample.cancer_type,
        "sampling_timepoint": sample.sampling_timepoint,
        "total_cfdna_ng_ml": sample.total_cfdna_ng_ml,
        "tumor_fraction_pct": sample.tumor_fraction_pct,
        "mrd_status": sample.mrd_status,
        "fragment_short_ratio": sample.fragment_short_ratio,
        "median_fragment_length_bp": sample.median_fragment_length_bp,
        "metadata": sample.sample_metadata_json,
        "size_distributions": [
            {
                "id": b.id,
                "bin_start_bp": b.bin_start_bp,
                "bin_end_bp": b.bin_end_bp,
                "fragment_count": b.fragment_count,
                "fragment_frequency_pct": b.fragment_frequency_pct,
            }
            for b in bins
        ],
        "end_motifs": [
            {
                "id": m.id,
                "motif_sequence_4mer": m.motif_sequence_4mer,
                "observed_frequency": m.observed_frequency,
                "reference_frequency": m.reference_frequency,
                "motif_diversity_score": m.motif_diversity_score,
            }
            for m in motifs
        ]
    }
