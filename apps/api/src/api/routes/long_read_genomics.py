"""API Routes for NGS Long-Read Structural Variant & Telomere Calling."""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.long_read_genomics_repo import LongReadGenomicsRepository
from research.genomics.long_read_engine import LongReadGenomicsEngine

router = APIRouter(prefix="/long-read", tags=["NGS Long-Read & Telomere Genomics"])


class LongReadAnalyzeRequest(BaseModel):
    sample_name: str = Field(..., description="Sample identifier")
    platform: str = Field(default="PACBIO_HIFI", description="Platform: PACBIO_HIFI, ONT_PROMETHION")
    target_gigabases: float = Field(default=50.0, ge=1.0, le=500.0)
    flowcell_type: str = Field(default="PromethION_R10.4.1")


@router.post("/analyze", status_code=status.HTTP_201_CREATED)
async def analyze_long_read_run(
    request: LongReadAnalyzeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Execute long-read sequencing analysis, SV calling, and telomere profiling."""
    engine = LongReadGenomicsEngine()
    analysis = engine.analyze_sequencing_run(
        sample_name=request.sample_name,
        platform=request.platform,
        target_gigabases=request.target_gigabases,
        flowcell_type=request.flowcell_type,
    )

    repo = LongReadGenomicsRepository(db)
    run_info = analysis["run"]
    run = await repo.create_run(
        sample_name=run_info["sample_name"],
        platform=run_info["platform"],
        flowcell_type=run_info["flowcell_type"],
        mean_read_length_bp=run_info["mean_read_length_bp"],
        total_gigabases=run_info["total_gigabases"],
        n50_length_bp=run_info["n50_length_bp"],
        mean_phred_quality=run_info["mean_phred_quality"],
        run_metadata_json={"mean_telomere_length_kbp": run_info["mean_telomere_length_kbp"]},
    )

    for sv in analysis["structural_variants"]:
        await repo.add_structural_variant(
            run_id=run.id,
            chromosome=sv["chromosome"],
            start_pos=sv["start_pos"],
            end_pos=sv["end_pos"],
            sv_type=sv["sv_type"],
            sv_length_bp=sv["sv_length_bp"],
            genotype=sv["genotype"],
            support_reads=sv["support_reads"],
            filter_status=sv["filter_status"],
        )

    for tel in analysis["telomeric_profiles"]:
        await repo.add_telomere_profile(
            run_id=run.id,
            chromosome_arm=tel["chromosome_arm"],
            hexamer_motif=tel["hexamer_motif"],
            repeat_count=tel["repeat_count"],
            telomere_length_kbp=tel["telomere_length_kbp"],
            erosion_hazard_level=tel["erosion_hazard_level"],
        )

    saved_run = await repo.get_run(run.id)
    return {
        "status": "success",
        "id": run.id,
        "sample_name": run.sample_name,
        "platform": run.platform,
        "n50_length_bp": run.n50_length_bp,
        "mean_phred_quality": run.mean_phred_quality,
        "structural_variants_count": len(saved_run.structural_variants if saved_run else []),
        "telomere_profiles_count": len(saved_run.telomeric_profiles if saved_run else []),
    }


@router.get("/runs")
async def list_long_read_runs(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """List recent long-read sequencing runs."""
    repo = LongReadGenomicsRepository(db)
    runs = await repo.list_runs(limit=limit)
    return [
        {
            "id": r.id,
            "sample_name": r.sample_name,
            "platform": r.platform,
            "mean_read_length_bp": r.mean_read_length_bp,
            "total_gigabases": r.total_gigabases,
            "n50_length_bp": r.n50_length_bp,
            "mean_phred_quality": r.mean_phred_quality,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "structural_variants_count": len(r.structural_variants),
            "telomere_profiles_count": len(r.telomeric_profiles),
        }
        for r in runs
    ]


@router.get("/runs/{run_id}")
async def get_long_read_run(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Get full details of a long-read sequencing run including SVs and telomere repeats."""
    repo = LongReadGenomicsRepository(db)
    run = await repo.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Long-read run not found")

    return {
        "id": run.id,
        "sample_name": run.sample_name,
        "platform": run.platform,
        "flowcell_type": run.flowcell_type,
        "mean_read_length_bp": run.mean_read_length_bp,
        "total_gigabases": run.total_gigabases,
        "n50_length_bp": run.n50_length_bp,
        "mean_phred_quality": run.mean_phred_quality,
        "structural_variants": [
            {
                "id": sv.id,
                "chromosome": sv.chromosome,
                "start_pos": sv.start_pos,
                "end_pos": sv.end_pos,
                "sv_type": sv.sv_type,
                "sv_length_bp": sv.sv_length_bp,
                "genotype": sv.genotype,
                "support_reads": sv.support_reads,
                "filter_status": sv.filter_status,
            }
            for sv in run.structural_variants
        ],
        "telomeric_profiles": [
            {
                "id": tel.id,
                "chromosome_arm": tel.chromosome_arm,
                "hexamer_motif": tel.hexamer_motif,
                "repeat_count": tel.repeat_count,
                "telomere_length_kbp": tel.telomere_length_kbp,
                "erosion_hazard_level": tel.erosion_hazard_level,
            }
            for tel in run.telomeric_profiles
        ],
    }
